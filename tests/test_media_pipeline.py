import os
import shutil
import tempfile
import unittest
import wave
from unittest.mock import patch

import app


class MediaPipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.old_asset_dir = app.ASSET_DIR
        app.ASSET_DIR = self.temp_dir.name

    def tearDown(self):
        app.ASSET_DIR = self.old_asset_dir
        self.temp_dir.cleanup()

    def test_studio_root_route_serves_index_html(self):
        response = app.root()
        self.assertEqual(response.path, "index.html")

    def test_music_generator_writes_valid_wav(self):
        result = app.generate_music({"mood": "Hopeful", "duration": 5})
        path = app.safe_asset(result["filename"])
        self.assertTrue(os.path.isfile(path))
        with wave.open(path, "rb") as audio:
            self.assertEqual(audio.getnchannels(), 1)
            self.assertEqual(audio.getframerate(), 22050)
            self.assertGreater(audio.getnframes(), 0)
        self.assertTrue(result["url"].startswith("/assets/"))

    def test_image_generation_rejects_invalid_dimensions_before_network(self):
        with patch.object(app, "urlopen") as request:
            with self.assertRaisesRegex(RuntimeError, "width and height"):
                app.generate_image({"prompt": "A quiet street", "width": 999, "height": 512})
            request.assert_not_called()

    def test_image_generation_rejects_excessive_steps(self):
        with patch.object(app, "urlopen") as request:
            with self.assertRaisesRegex(RuntimeError, "steps"):
                app.generate_image({"prompt": "A quiet street", "steps": 100})
            request.assert_not_called()

    def test_comfyui_workflow_placeholders_are_replaced_recursively(self):
        source = {"1": {"inputs": {"text": "{{prompt}}", "image": "{{image}}", "frames": "{{frames}}"}}}
        result = app._replace_workflow_values(source, {"prompt": "A quiet scene", "image": "scene.png", "frames": 49})
        self.assertEqual(result["1"]["inputs"]["text"], "A quiet scene")
        self.assertEqual(result["1"]["inputs"]["image"], "scene.png")
        self.assertEqual(result["1"]["inputs"]["frames"], 49)

    def test_comfyui_workflow_preserves_numeric_placeholder_types(self):
        source = {"1": {"inputs": {"width": "{{width}}", "prompt": "Scene {{prompt}}"}}}
        result = app._replace_workflow_values(source, {"width": 768, "prompt": "A quiet scene"})
        self.assertEqual(result["1"]["inputs"]["width"], 768)
        self.assertIsInstance(result["1"]["inputs"]["width"], int)
        self.assertEqual(result["1"]["inputs"]["prompt"], "Scene A quiet scene")

    def test_comfyui_video_output_finder_ignores_non_video_files(self):
        history = {"outputs": {
            "1": {"images": [{"filename": "preview.png"}]},
            "2": {"files": [{"filename": "frame.webp"}]},
            "3": {"gifs": [{"filename": "final.mp4", "type": "output"}]}
        }}
        self.assertEqual(app._find_comfyui_video(history)["filename"], "final.mp4")

    def test_comfyui_video_output_finder_returns_none_without_video(self):
        history = {"outputs": {"1": {"images": [{"filename": "preview.png"}]}}}
        self.assertIsNone(app._find_comfyui_video(history))

    def test_comfyui_video_requires_explicit_server_configuration(self):
        with patch.object(app, "COMFYUI_URL", ""):
            with self.assertRaisesRegex(RuntimeError, "MYTUBE_COMFYUI_URL"):
                app.generate_comfyui_video({"prompt": "A scene"})

    def test_generated_audio_path_is_confined_to_audio_directory(self):
        path = app.safe_audio("preview.wav")
        self.assertEqual(os.path.dirname(path), os.path.abspath("generated_audio"))

    def test_asset_path_stays_inside_asset_directory(self):
        path = app.safe_asset("../example.wav")
        self.assertEqual(os.path.dirname(path), os.path.abspath(self.temp_dir.name))

    @unittest.skipUnless(shutil.which("ffmpeg"), "FFmpeg is not installed")
    def test_video_and_mux_export_from_generated_assets(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow is not installed")
        Image.new("RGB", (64, 64), "navy").save(app.safe_asset("scene.png"))
        video = app.render_video({"images": ["scene.png"], "secondsPerImage": 2})
        self.assertTrue(os.path.isfile(app.safe_asset(video["filename"])))
        music = app.generate_music({"mood": "Suspense", "duration": 5})
        export = app.mux_export({"video": video["filename"], "audio": music["filename"]})
        self.assertTrue(os.path.isfile(app.safe_asset(export["filename"])))
        self.assertGreater(os.path.getsize(app.safe_asset(export["filename"])), 0)


if __name__ == "__main__":
    unittest.main()
