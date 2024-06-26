import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import random,string,json,os,sys
from skimage.filters import gaussian
import shutil
from moviepy.editor import *
from pathlib import Path

def move_mp4_files_to_video_folder():
    destination_folder = './VIDEO'
    os.makedirs(destination_folder, exist_ok=True)
    current_directory = os.getcwd()
    files = os.listdir(current_directory)
    for file in files:
        if file.endswith('.mp4'):
            source = os.path.join(current_directory, file)
            destination = os.path.join(destination_folder, file)
            shutil.move(source, destination)
            print(f"Moved {file} to {destination_folder}")

def empty_folder(folder_path):
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isfile(item_path):
            os.remove(item_path)
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)

def main():

    def tryremove(file):
        try:
            os.remove(file)
        except Exception as e:
            return e
    def clean():
        pass

    clean()
    tryremove("./VIDEO/.DS_Store")
    tryremove("./US/.DS_Store")
    donefiles=[]

    afps=[-1,1]
    angles=[-3,3]
    settings = json.loads(open('settings.json','r').read())
    randeffectslimit=settings['rel']
    doRotate = settings['doRotate']
    doBlurIn = settings['doBlurIn']
    doMirror = settings['doMirror']
    vidc = settings['vidc']
    mind = settings['mind']
    maxd = settings['maxd']
    showEffect = settings['showEffect']
    doblur = settings['doblur']
    blursigma = settings['blursigma']

    def create_file_list(folder):
        return [str(f) for f in Path(folder).iterdir()]

    def create_image_list(folder):
        image_list=[]
        folder = Path(folder)
        if folder.is_file():
            image = ImageClip(str(folder),duration=1)
            image_list.append(image)
        if folder.is_dir():
            for file in sorted(folder.iterdir(), reverse=True):
                image = ImageClip(str(file),duration=1)
                image_list.append(image)
        return image_list

    def filename(folder):
        file_name = ''.join(random.choice(string.ascii_lowercase) for i in range(5))
        file_name = str(Path(folder).joinpath(file_name + '.mp4'))
        return file_name

    def filenamepre(folder):
        file_name = ''.join(random.choice(string.ascii_lowercase) for i in range(5))
        file_name = str(Path(foldertmp).joinpath(file_name + '-PRE.mp4'))
        return file_name

    def filenameprepre(folder):
        file_name = ''.join(random.choice(string.ascii_lowercase) for i in range(5))
        file_name = str(Path(foldertmp).joinpath(file_name + '-PRE-pre.mp4'))
        return file_name

    def blur(image):
        return gaussian(image.astype(float), sigma=blursigma)

    result_folder = os.path.join(sys.argv[0].replace("main.py",""),'US')
    foldertmp = os.path.join(sys.argv[0].replace("main.py",""),'TEMP')

    images = create_image_list(r'./PNG')

    video_ls = create_file_list(os.path.join(sys.argv[0].replace("main.py",""),'VIDEO'))
    print(result_folder)

    unq_filter_params =["colorbalance=rs=.3","colorbalance=gs=-0.20","colorbalance=gs=0.20","colorbalance=bs=-0.30","colorbalance=bs=0.30","colorbalance=rm=0.30","colorbalance=rm=-0.30","colorbalance=gm=-0.25","colorbalance=bm=-0.25","colorbalance=rh=-0.15","colorbalance=gh=-0.20","colorbalance=bh=-0.20"]
    noises=[10,12,14,15]
    for video in video_ls:
        for vvv in range(0,vidc):
            noises_var=[['-vf',f'noise=c0s={random.choice(noises)}:c0f=t+u']]
            print(f"Processing video {vvv+1}/{vidc}")
            clip = VideoFileClip(video)
            if doRotate:
                print("Preparing..")
                fnpre=filenameprepre(result_folder)
                clip.write_videofile(fnpre,ffmpeg_params=["-vf",f"rotate={random.choice(angles)}*PI/180"])
                print("Closed")
                clip = VideoFileClip(fnpre)
            clip=clip.set_fps(clip.fps+random.choice(afps))
            rmaxd=maxd
            if(clip.duration < maxd):
                rmaxd=clip.duration

            if showEffect:
                clip = vfx.fadein(clip, duration=2)
            if doMirror:
                clip_mirror = vfx.mirror_x(clip)
            else:
                clip_mirror=clip
            if doblur:
                print("blurring..")
                clip_mirror=clip.fl_image(blur)
            if doBlurIn:
                print("blur first sec")
                smclip=clip_mirror.subclip(0,1)
                ogclip=clip_mirror.subclip(1,clip_mirror.duration)
                smclip=smclip.fl_image(blur)
                clip_mirror=concatenate_videoclips([smclip,ogclip])
                print("done!")
            
            fn=filenamepre(result_folder)
            oneparam=""
            unq_filter_paramsstr=[]
            for i in range(0,randeffectslimit):
                unq_filter_paramsstr.append(random.choice(unq_filter_params))
            unq_filter_paramsstr=','.join(unq_filter_paramsstr)
            if(unq_filter_paramsstr!="" and unq_filter_paramsstr!=[]):
                oneparam="-filter_complex"
            if(len(video.split(".png."))==2 or len(video.split(".jpg."))==2 or len(video.split(".jpeg."))==2 or len(video.split(".bmp."))==2):
                unq_filter_paramsstr=""
                oneparam=""
            clip=clip_mirror
            addargs=[oneparam,unq_filter_paramsstr]
            if(addargs[0] == "" or addargs[1] ==""):
                addargs=[]
            clip.write_videofile(fn, ffmpeg_params=['-fflags','+bitexact','-flags:v','+bitexact','-flags:a','+bitexact']+addargs)
            new_video=VideoFileClip(fn)
            clip=new_video
            print("--------------------------------------------------------------------------------------------------------------")
            fffn=filename(result_folder)
            print(fffn)
            print(result_folder)
            if(len(video.split(".png."))==2 or len(video.split(".jpg."))==2 or len(video.split(".jpeg."))==2 or len(video.split(".bmp."))==2):
                new_video.write_videofile(fffn,ffmpeg_params=["-c:a","aac"])
            else:
                new_video.write_videofile(fffn, ffmpeg_params=random.choice(noises_var)+["-c:a","aac"])
            donefiles.append(fffn)
            print(fffn)
            current_path = os.getcwd()
            empty_folder(f'{current_path}/TEMP')

    print("Done! Filenames:")
    for fn in donefiles:
        print(fn)

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')

async def run(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data['waiting_for_videos'] = True
    context.user_data['video_count'] = 0
    await update.message.reply_text("Please send your videos. Send /done when you're done.")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"saving video {context.user_data['video_count']+1}")
    if context.user_data.get('waiting_for_videos'):
        video = update.message.video
        if video:
            context.user_data['video_count'] += 1
            file = await context.bot.get_file(video.file_id)
            file_path = f"downloaded_video_{context.user_data['video_count']}_{video.file_id}.mp4"
            await file.download_to_drive(file_path)
            await update.message.reply_text(f"Video {context.user_data['video_count']} saved.")
            move_mp4_files_to_video_folder()
        else:
            await update.message.reply_text("That wasn't a video. Please send a video or /done to finish.")

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get('waiting_for_videos'):
        context.user_data['waiting_for_videos'] = False
        await update.message.reply_text(f"Total videos received: {context.user_data['video_count']}")
        await update.message.reply_text(f"Processing the Video(s)")
        main()
        us_folder = "./US"
        if os.path.exists(us_folder) and os.path.isdir(us_folder):
            video_files = [f for f in os.listdir(us_folder) if f.endswith(('.mp4', '.avi', '.mov'))]
            if video_files:
                await update.message.reply_text("Sending created videos")
                for video_file in video_files:
                    video_path = os.path.join(us_folder, video_file)
                    await context.bot.send_video(chat_id=update.effective_chat.id, video=open(video_path, 'rb'))
                await update.message.reply_text("All videos sent.")
                current_path = os.getcwd()
                empty_folder(f'{current_path}/US')
                empty_folder(f'{current_path}/TEMP')
                empty_folder(f'{current_path}/VIDEO')
            else:
                await update.message.reply_text("No videos found.")
        else:
            await update.message.reply_text("The US folder does not exist.")
    else:
        await update.message.reply_text("No video reception in progress.")

app = ApplicationBuilder().token("7314793596:AAHDorVX4SI8XF7Mb3s7G7-n560UrXwXt74").build()
app.add_handler(CommandHandler("hello", hello))
app.add_handler(CommandHandler("run", run))
app.add_handler(CommandHandler("done", done))
app.add_handler(MessageHandler(filters.VIDEO, handle_video))
app.run_polling()