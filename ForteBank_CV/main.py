import argparse
from pathlib import Path
from video_processor import get_video_info
from evidence_generator import evidence_for_event

parser = argparse.ArgumentParser(description='ForteBank evidence extraction demo')
parser.add_argument('--video',required=True,help='Path to a .mov video')
parser.add_argument('--time',required=True,type=float,help='Event timestamp in seconds')
args=parser.parse_args()
print('Video:',get_video_info(args.video))
frames=evidence_for_event(args.video,args.time)
print(f'Extracted {len(frames)} JPEG evidence frames into evidence/')
for f in frames:
    print('Timestamp:',f['timestamp_sec'],'base64 length:',len(f['image_base64']))
