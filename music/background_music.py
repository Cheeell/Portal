# ===========================================
# FILE: music/background_music.py
# ===========================================
import os
import threading
import random

# Directory for built-in background music
MUSIC_DIR = "music"
if not os.path.exists(MUSIC_DIR):
    os.makedirs(MUSIC_DIR)


class BackgroundMusicManager:
    def __init__(self):
        self.is_playing = False
        self.current_track = None
        self.playlist = []
        self.playback_thread = None
        self.volume = 0.5
        self.loop_playlist = True
        self.shuffle = False
        self.current_index = 0

    def scan_music_folder(self):
        """Scan music folder for audio files"""
        supported_formats = ['.mp3', '.wav', '.ogg', '.flac', '.m4a']
        self.playlist = []

        if os.path.exists(MUSIC_DIR):
            for filename in os.listdir(MUSIC_DIR):
                if any(filename.lower().endswith(ext) for ext in supported_formats):
                    self.playlist.append(os.path.join(MUSIC_DIR, filename))

        if self.shuffle:
            random.shuffle(self.playlist)

        return len(self.playlist)

    def play(self):
        """Start playing background music"""
        if self.is_playing:
            return

        try:
            import pygame

            # Initialize pygame mixer if not already initialized
            if not pygame.mixer.get_init():
                pygame.mixer.init()

            # Scan for music files
            track_count = self.scan_music_folder()
            if track_count == 0:
                print("⚠️ No music files found in music/ folder")
                return False

            self.is_playing = True
            self.current_index = 0

            # Start playback thread
            self.playback_thread = threading.Thread(target=self._playback_loop, daemon=True)
            self.playback_thread.start()

            print(f"🎵 Background music started ({track_count} tracks)")
            return True

        except ImportError:
            print("❌ pygame not installed. Install with: pip install pygame")
            return False
        except Exception as e:
            print(f"❌ Error starting background music: {e}")
            return False

    def _playback_loop(self):
        """Main playback loop running in background thread"""
        import pygame

        while self.is_playing and len(self.playlist) > 0:
            # Get current track
            if self.current_index >= len(self.playlist):
                if self.loop_playlist:
                    self.current_index = 0
                    if self.shuffle:
                        random.shuffle(self.playlist)
                else:
                    self.is_playing = False
                    break

            track_path = self.playlist[self.current_index]
            self.current_track = os.path.basename(track_path)

            try:
                # Load and play track
                pygame.mixer.music.load(track_path)
                pygame.mixer.music.set_volume(self.volume)
                pygame.mixer.music.play()

                print(f"🎵 Now playing: {self.current_track}")

                # Wait for track to finish
                while pygame.mixer.music.get_busy() and self.is_playing:
                    pygame.time.Clock().tick(10)

                # Move to next track
                self.current_index += 1

            except Exception as e:
                print(f"❌ Error playing {self.current_track}: {e}")
                self.current_index += 1

        self.is_playing = False
        self.current_track = None
        print("🎵 Background music stopped")

    def stop(self):
        """Stop background music"""
        if not self.is_playing:
            return

        try:
            import pygame
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()

            self.is_playing = False
            self.current_track = None
            print("🎵 Background music stopped")

        except ImportError:
            pass
        except Exception as e:
            print(f"❌ Error stopping music: {e}")

    def set_volume(self, volume):
        """Set music volume (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))

        try:
            import pygame
            if pygame.mixer.get_init():
                pygame.mixer.music.set_volume(self.volume)
        except:
            pass

    def next_track(self):
        """Skip to next track"""
        if not self.is_playing:
            return

        try:
            import pygame
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
        except:
            pass

    def toggle_shuffle(self):
        """Toggle shuffle mode"""
        self.shuffle = not self.shuffle
        if self.shuffle and len(self.playlist) > 0:
            random.shuffle(self.playlist)
        return self.shuffle

    def toggle_loop(self):
        """Toggle loop mode"""
        self.loop_playlist = not self.loop_playlist
        return self.loop_playlist

    def get_status(self):
        """Get current playback status"""
        return {
            "is_playing": self.is_playing,
            "current_track": self.current_track,
            "track_count": len(self.playlist),
            "volume": self.volume,
            "shuffle": self.shuffle,
            "loop": self.loop_playlist,
            "current_index": self.current_index
        }


# Global music manager instance
_music_manager = None


def get_music_manager():
    """Get or create global music manager instance"""
    global _music_manager
    if _music_manager is None:
        _music_manager = BackgroundMusicManager()
    return _music_manager