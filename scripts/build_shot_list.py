"""Generate shot-list.jsonl, shot-list.md, talks.jsonl from dense 1fps classification.

Shot-type codes (user's 7 categories):
  1 = ultra-wide storefront + whole poster/banner (exterior establishing)
  2 = secondary wide, one screen / one poster
  3 = interior ultra-wide (wide shot inside the cafe showing the room)
  4 = interior person close-up
  5 = interior audience close-up
  6 = hands/items close-up
  7 = timelapse
  U = uncertain (cannot confidently classify this frame)

Segments are [start_sec, end_sec) in seconds; frame-0001 = t=0s.
Every clip's segments must partition [0, n_frames) exactly (validated below).
"""
import glob, json, os
from collections import Counter

ROOT = os.path.expanduser('~/workspace/inkling-recap')
FRAMES = os.path.join(ROOT, 'frames-dense')
MEDIA = os.path.join(ROOT, 'media', 'DJI_001')

NAMES = {
    '1': 'ultra-wide storefront + whole poster/banner',
    '2': 'secondary wide, one screen / one poster',
    '3': 'interior ultra-wide',
    '4': 'interior person close-up',
    '5': 'interior audience close-up',
    '6': 'hands/items close-up',
    '7': 'timelapse',
    'U': 'uncertain',
}

# clip -> list of (start, end, code, description, confidence)
SEG = {
'DJI_20260719072352_0033_D': [(0,66,'3','Man in striped shirt presents at the big screen, audience seated; screen shows Chinese AI-native tools slides','confident')],
'DJI_20260719072707_0034_D': [(0,69,'3','Same striped-shirt presenter continues; screen shows a dashboard with QR code, audience filming with phones','confident')],
'DJI_20260719073634_0037_D': [(0,50,'3','Man in black tee with glasses presents a website on screen ("Taste your wild..."), audience seated','confident'),
                              (50,56,'5','Camera pans to a close-up of audience members watching','confident')],
'DJI_20260719074342_0038_D': [(0,14,'3','Man in black tee with glasses continues presenting at the screen, audience seated','confident'),
                              (14,18,'U','Camera swings fast toward the glass door; frames are motion-blurred, shot type not readable','uncertain'),
                              (18,32,'3','Back to the wide room; presenter at the screen, audience seated','confident')],
'DJI_20260719082251_0039_D': [(0,15,'3','Man in light shirt presents at a screen showing a dark UI, audience seated','confident'),
                              (15,44,'2','Camera moves in; the screen (dark product UI) fills the frame','confident')],
'DJI_20260719082925_0040_D': [(0,20,'3','Man in grey shirt with glasses holds a mic and speaks; audience seated, screen with text behind him','confident'),
                              (20,77,'4','Camera moves closer; medium close-up of the grey-shirt presenter speaking into the mic','confident')],
'DJI_20260719084815_0042_D': [(0,10,'3','Woman in green tee and cap holds a mic at a screen showing a phone app, audience seated','confident'),
                              (10,28,'5','Crowd/audience close-up; people standing and watching near the glass (CURSOR logo reversed)','confident'),
                              (28,76,'4','Close-up of the woman presenter (green tee, cap) speaking into the mic beside the phone-app screen','confident')],
'DJI_20260719091529_0043_D': [(0,63,'3','Woman in white sleeveless top presents at the screen ("Your agents work..."), audience seated at tables','confident')],
'DJI_20260719091607_0001_D': [(0,7,'4','Man in white tee and khaki shorts works on a laptop setting up the screen; a blonde woman points at the screen','confident')],
'DJI_20260719091652_0002_D': [(0,7,'6','Close-up of hands and drink bottles/cups on the bar counter; a hand reaches for a cup','confident')],
'DJI_20260719091709_0003_D': [(0,7,'4','Man in navy polo and cap types on a laptop at a small table; woman in white lace on her phone; man standing by the door','confident')],
'DJI_20260719091907_0004_D': [(0,6,'3','Wide room; screen with text, audience seated at tables','confident')],
'DJI_20260719092043_0007_D': [(0,3,'5','Close-up of audience members (man in cap, woman, young man holding a camera/gimbal)','confident'),
                              (3,13,'3','Wide room; presenter (man in white tee) at the screen, audience seated','confident')],
'DJI_20260719092253_0008_D': [(0,13,'3','Presenter (man in white tee) at the screen, audience seated at tables','confident'),
                              (13,16,'5','Close-up of audience members (man in cap, woman) watching','confident')],
'DJI_20260719092424_0044_D': [(0,65,'3','Presenter (man in white tee with red logo) holds a mic and demos code on the screen; audience seated, some smiling','confident')],
'DJI_20260719092510_0009_D': [(0,3,'5','Close-up of people near the door (blonde woman, man with glasses)','confident'),
                              (3,10,'3','Wide room; presenter at the screen, audience seated','confident')],
'DJI_20260719092652_0010_D': [(0,9,'3','Wide room; screen with text, audience seated','confident'),
                              (9,12,'4','Close-up of two men by the glass door (CURSOR logo reversed on the glass)','confident')],
'DJI_20260719092946_0011_D': [(0,6,'4','People at the door; a woman looks at her phone, a man leans in to talk','confident'),
                              (6,8,'3','Wider room view; screen and audience','confident')],
'DJI_20260719094253_0020_D': [(0,12,'3','Wide room; screen showing code/dashboard, audience seated','confident')],
'DJI_20260719094321_0021_D': [(0,10,'3','Wide room; screen with code, audience seated','confident')],
'DJI_20260719094634_0022_D': [(0,3,'2','The CURSOR logo on the glass door/window fills the frame','confident'),
                              (3,7,'3','Interior wide; a man in the foreground, blonde woman, audience seated','confident')],
'DJI_20260719094653_0023_D': [(0,2,'2','The CURSOR logo on the glass fills the frame','confident'),
                              (2,8,'3','Interior wide; blonde woman in pink top and audience, screen in the back','confident')],
'DJI_20260719094910_0025_D': [(0,5,'4','EXTERIOR street: close-up of people outside (woman with a phone, men chatting) under the plane trees. Note: category 4 is labelled interior; this is the closest fit, exterior people close-up.','confident')],
'DJI_20260719095441_0026_D': [(0,8,'1','EXTERIOR: black CURSOR banner ("Cursor Cafe x Sunset Shanghai") and the whole storefront, crowd at the door','confident')],
'DJI_20260719095456_0027_D': [(0,14,'1','EXTERIOR: storefront entrance, glass doors, awning, people at the door','confident')],
'DJI_20260719095849_0028_D': [(0,13,'3','Wide room; screen with code, audience seated','confident'),
                              (13,15,'5','Close-up of an audience member (man in North Face shirt)','confident')],
'DJI_20260719095919_0029_D': [(0,12,'3','Presenter (man in white shirt) at a screen with code; audience leaning in, Q&A feel','confident')],
'DJI_20260719100427_0031_D': [(0,14,'3','Wide room; screen with a settings/UI window, presenter (man in white shirt) seated at a laptop, audience','confident')],
'DJI_20260719100747_0032_D': [(0,11,'1','EXTERIOR: two hosts by the black CURSOR banner giving thumbs up, crowd at the door','confident')],
'DJI_20260719100911_0033_D': [(0,6,'4','EXTERIOR street: people close-up (men chatting, banana leaves, awning). Note: exterior people close-up; category 4 is the closest fit.','confident')],
'DJI_20260719100954_0034_D': [(0,18,'4','EXTERIOR street: people chatting (woman in white dress, men), plane trees. Note: exterior people close-up.','confident')],
'DJI_20260719101128_0035_D': [(0,8,'4','EXTERIOR street: people (man with a camera, woman on her phone). Note: exterior people close-up.','confident')],
'DJI_20260719101206_0036_D': [(0,16,'3','Presenter (man in light shirt) at a screen showing a website ("Shim by feel" product page), audience seated','confident')],
'DJI_20260719101336_0037_D': [(0,10,'1','EXTERIOR: whole storefront and awning, people at the door, street with plane trees','confident')],
'DJI_20260719101711_0039_D': [(0,4,'4','Woman in black (staff) in the foreground, audience seated behind her','confident'),
                              (4,12,'3','Wider room view; audience seated, blue screen in the back','confident')],
'DJI_20260719101751_0040_D': [(0,7,'3','Presenter (man in black tee) at a screen showing a phone UI/app, audience seated, some on laptops','confident')],
'DJI_20260719101843_0042_D': [(0,8,'1','EXTERIOR: black CURSOR banner ("Cursor Cafe x Sunset Shanghai") and storefront; man in white tee giving thumbs up, crowd','confident')],
'DJI_20260719102228_0044_D': [(0,7,'3','Presenter (man in blue polo and cap) at a screen, audience seated','confident')],
'DJI_20260719102949_0045_D': [(0,9,'3','Presenter (man in blue polo) wrapping up; audience seated, camera behind a man with a backpack','confident')],
'DJI_20260719103139_0046_D': [(0,15,'3','Screen playing a video/animation; audience watching, presenter (man in light shirt) at the side','confident')],
'DJI_20260719103214_0047_D': [(0,4,'3','Crowd; a man with a camera, the screen in the back','confident')],
'DJI_20260719103250_0048_D': [(0,7,'3','Presenter (man in light blue shirt) at a screen showing the "AI Mi" app download page, audience seated','confident')],
'DJI_20260719103600_0049_D': [(0,12,'3','Presenter (man in light blue shirt) at a screen showing "Pairoa" (blue landing page), audience leaning in','confident')],
'DJI_20260719103621_0050_D': [(0,11,'3','Presenter (man in light blue shirt) at the Pairoa screen, gesturing; an audience member gestures back (Q&A)','confident')],
'DJI_20260719103816_0051_D': [(0,19,'3','Presenter (man in light blue shirt) at a laptop, screen with a UI; the audience laughs - the laughter moment','confident')],
'DJI_20260719104335_0052_D': [(0,11,'3','Crowd; blonde woman (pink top) in the foreground, people at tables, a fan','confident')],
'DJI_20260719104354_0053_D': [(0,7,'5','Close-up of audience members at a table chatting (men, a fan)','confident')],
'DJI_20260719104432_0054_D': [(0,7,'4','EXTERIOR street: four people chatting under the plane trees. Note: exterior people close-up.','confident')],
'DJI_20260719104548_0055_D': [(0,6,'4','EXTERIOR street: people outside the shop under the awning; woman in white lace, man with a coffee cup. Note: exterior people close-up.','confident')],
'DJI_20260719104626_0056_D': [(0,2,'5','Close-up of people at the bar (woman with a phone, men)','confident'),
                              (2,7,'3','Wider room; a woman presenter (blonde, pink top) at the screen, audience seated','confident')],
'DJI_20260719104647_0057_D': [(0,7,'3','Man in white shirt seated; screen showing a blue "no signal"/settings page, audience seated','confident')],
'DJI_20260719105222_0058_D': [(0,5,'4','EXTERIOR street: people under the plane trees. Note: exterior people close-up.','confident')],
'DJI_20260719110516_0059_D': [(0,10,'3','Presenter (man in beige tee and light shorts) at a screen: "Your agents work. You are sleeping." with a watch graphic; audience seated','confident')],
'DJI_20260719110541_0060_D': [(0,9,'3','Same beige-tee presenter continues; screen "Your agents work", audience seated','confident')],
'DJI_20260719110749_0061_D': [(0,6,'3','Presenter (beige tee) at a screen showing "ARIAVA" with QR codes, audience seated','confident')],
'DJI_20260719110926_0062_D': [(0,9,'3','Presenter (beige tee) at the ARIAVA screen with QR codes; an audience member points at the screen (Q&A)','confident')],
'DJI_20260719111025_0063_D': [(0,4,'5','Close-up of audience (man in green shirt, others)','confident'),
                              (4,13,'3','Wider view; presenter (beige tee) at the ARIAVA screen, audience seated','confident')],
'DJI_20260719111212_0064_D': [(0,4,'5','Group standing near the bar (men, a woman)','confident'),
                              (4,15,'3','Presenter (beige tee) at the ARIAVA screen, audience seated','confident')],
'DJI_20260719113019_0067_D': [(0,7,'3','Presenter (man in dark tee) at a screen showing a phone AI app (Chinese text), audience seated','confident')],
'DJI_20260719113657_0068_D': [(0,5,'3','Presenter (man in dark tee) at a screen with a UI, audience seated','confident')],
'DJI_20260719113730_0069_D': [(0,10,'3','Presenter (man in dark tee) at a screen, audience seated','confident')],
'DJI_20260719113836_0070_D': [(0,3,'4','Man in beige tee standing by the glass door','confident'),
                              (3,12,'3','Presenter (man in dark tee) at the screen, audience seated','confident')],
'DJI_20260719115203_0073_D': [(0,8,'3','Presenter (man in light shirt) at a screen playing a video (person outdoors/nature), audience watching','confident')],
'DJI_20260719115456_0074_D': [(0,4,'4','People at the door (man in white tee, others)','confident'),
                              (4,8,'2','The CURSOR logo on the glass fills the frame','confident'),
                              (8,12,'3','Interior wide; blonde woman and audience, screen in the back','confident')],
'DJI_20260719120831_0075_D': [(0,9,'3','Young man in purple shirt seated at a laptop; screen with code, audience seated','confident')],
'DJI_20260719121456_0077_D': [(0,6,'3','Man at a screen showing a video/photo, audience watching','confident')],
'DJI_20260719122116_0079_D': [(0,4,'1','EXTERIOR: black CURSOR banner ("Cursor Cafe x Sunset Shanghai"); woman in black giving thumbs up, people at the door','confident')],
'DJI_20260719122153_0080_D': [(0,4,'1','EXTERIOR: woman in white lace dress by the black CURSOR banner, people at the door','confident')],
}

def main():
    import subprocess
    clips = sorted(os.listdir(FRAMES))
    # validate segments partition [0, n_frames)
    for c in clips:
        n = len(glob.glob(os.path.join(FRAMES, c, 'frame-*.jpg')))
        segs = SEG.get(c)
        assert segs, f"no segments for {c}"
        pos = 0
        for (s, e, code, desc, conf) in segs:
            assert s == pos, f"{c}: gap at {pos}, segment starts {s}"
            assert e > s, f"{c}: bad segment {s}-{e}"
            pos = e
        assert pos == n, f"{c}: segments end at {pos}, frames={n}"
    print(f"validated {len(clips)} clips")

    # durations
    total_dur = 0.0
    dur = {}
    for c in clips:
        f = os.path.join(MEDIA, c + '.MP4')
        d = subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f],
                           capture_output=True, text=True).stdout.strip()
        dur[c] = float(d) if d else 0.0
        total_dur += dur[c]

    # write shot-list.jsonl (one row per frame)
    counts = Counter()
    conf_counts = Counter()
    rows = 0
    with open(os.path.join(ROOT, 'shot-list.jsonl'), 'w') as out:
        for c in clips:
            frames = sorted(glob.glob(os.path.join(FRAMES, c, 'frame-*.jpg')))
            for fp in frames:
                fname = os.path.basename(fp)
                sec = int(fname.replace('frame-', '').replace('.jpg', '')) - 1
                for (s, e, code, desc, conf) in SEG[c]:
                    if s <= sec < e:
                        counts[code] += 1
                        conf_counts[conf] += 1
                        out.write(json.dumps({
                            'clip': c + '.MP4',
                            'frame': fname,
                            'timestamp_sec': sec,
                            'shot_type': code,
                            'shot_type_name': NAMES[code],
                            'description': desc,
                            'confidence': conf,
                        }, ensure_ascii=False) + '\n')
                        rows += 1
                        break
    print(f"shot-list.jsonl: {rows} rows")
    print("per-type frame counts:", dict(sorted(counts.items())))
    print("confidence counts:", dict(conf_counts))
    print(f"total duration: {total_dur:.1f}s, effective fps: {rows/total_dur:.3f}")
    print(f"coverage: {len(clips)}/{len(clips)} clips have frames (100%)")
    # save metrics for the md builder
    json.dump({'clips': len(clips), 'frames': rows, 'duration': round(total_dur,1),
               'fps': round(rows/total_dur,3), 'counts': dict(sorted(counts.items())),
               'conf': dict(conf_counts)}, open('/tmp/shot_metrics.json','w'), indent=1)

if __name__ == '__main__':
    main()
