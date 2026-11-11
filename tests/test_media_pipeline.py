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
