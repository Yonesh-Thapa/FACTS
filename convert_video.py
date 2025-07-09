#!/usr/bin/env python3
"""
Video Converter Script for F.A.C.T.S
Converts MOV to MP4 for better web compatibility
"""

import os
import sys

def install_moviepy():
    """Install moviepy if not available"""
    try:
        import moviepy
        return True
    except ImportError:
        print("Installing moviepy for video conversion...")
        os.system("pip install moviepy")
        try:
            import moviepy
            return True
        except ImportError:
            print("Failed to install moviepy. Please install manually: pip install moviepy")
            return False

def convert_video():
    """Convert MOV to MP4"""
    if not install_moviepy():
        return False
    
    try:
        from moviepy.editor import VideoFileClip
        
        input_file = "static/videos/introVideo.mov"
        output_file = "static/videos/introVideo.mp4"
        
        if not os.path.exists(input_file):
            print(f"Error: {input_file} not found!")
            return False
        
        print(f"Converting {input_file} to {output_file}...")
        print("This may take a few minutes...")
        
        # Load the video
        clip = VideoFileClip(input_file)
        
        # Convert to MP4 with web-optimized settings
        clip.write_videofile(
            output_file,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            preset='medium',
            ffmpeg_params=['-movflags', '+faststart']  # Optimize for web streaming
        )
        
        # Clean up
        clip.close()
        
        print(f"✅ Conversion complete! MP4 file created: {output_file}")
        
        # Show file sizes
        mov_size = os.path.getsize(input_file) / (1024 * 1024)
        mp4_size = os.path.getsize(output_file) / (1024 * 1024)
        
        print(f"Original MOV: {mov_size:.1f} MB")
        print(f"Converted MP4: {mp4_size:.1f} MB")
        
        return True
        
    except Exception as e:
        print(f"Error during conversion: {e}")
        return False

if __name__ == "__main__":
    print("🎬 Video Converter for F.A.C.T.S")
    print("Converting MOV to MP4 for better web compatibility...")
    print()
    
    if convert_video():
        print("\n✅ Success! You can now use the MP4 file in your website.")
        print("The MP4 format will work better for autoplay across all devices.")
    else:
        print("\n❌ Conversion failed. You can still try using the MOV file,")
        print("but it may not autoplay on all devices/browsers.")
