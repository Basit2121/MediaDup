import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import random,string,json,os,sys
from skimage.filters import gaussian
import shutil
from moviepy.editor import *
from pathlib import Path
import random
from mutagen.mp4 import MP4
from faker import Faker
from telegram.ext import ContextTypes
import os
import uuid
import random
import string
from datetime import datetime
from PIL.PngImagePlugin import PngInfo
import win32_setctime
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
import numpy as np
import os
from PIL import Image

def convert_images_to_png(folder_path):
    supported_formats = ('.jpg', '.jpeg', '.bmp', '.gif', '.tiff')
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(supported_formats):
            file_path = os.path.join(folder_path, filename)
            with Image.open(file_path) as img:
                name_without_ext = os.path.splitext(filename)[0]
                new_filename = f"{name_without_ext}.png"
                new_file_path = os.path.join(folder_path, new_filename)
                img.save(new_file_path, 'PNG')
            os.remove(file_path)

def change_images():
    convert_images_to_png('IMAGES')
    folder_path = 'IMAGES'
    png_files = find_png_files(folder_path)

    with open("settings_image.txt", 'r') as file:
        dup_count = file.read()
    
    dup_count = int(dup_count)

    for i in range(dup_count):
        for images in png_files:
            input_path = f"IMAGES/{images}"
            characters = string.ascii_letters + string.digits  
            random_string = ''.join(random.choice(characters) for _ in range(10))
            make_unique_png(input_path, f'TEMP_IMG/{random_string}.png')
        
    folder_path = 'TEMP_IMG'
    png_files = find_png_files(folder_path)

    for images in png_files:
        input_path = f"TEMP_IMG/{images}"
        new_file_path = create_unique_png_duplicate(input_path, "OUTPUT")
        print(f"Unique duplicate created: {new_file_path}")

    for image in png_files:
        os.remove(f"TEMP_IMG/{image}")

def find_png_files(folder_path):
    png_files = []
    files = os.listdir(folder_path)
    for file in files:
        if os.path.isfile(os.path.join(folder_path, file)) and file.lower().endswith('.png'):
            png_files.append(file)
    return png_files

def make_unique_png(input_path, output_path):
    with Image.open(input_path) as img:
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        img_array = np.array(img)
        
        noise_intensity = random.uniform(1, 3)
        noise = np.random.randint(-int(noise_intensity), int(noise_intensity) + 1, img_array.shape)
        modified_array = np.clip(img_array.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        
        modified_img = Image.fromarray(modified_array)
        
        filters = [
            ImageFilter.SMOOTH,
            ImageFilter.EDGE_ENHANCE_MORE,
            ImageFilter.SHARPEN
        ]
        random_filter = random.choice(filters)
        modified_img = Image.blend(modified_img, modified_img.filter(random_filter), 0.5)
        
        rotation_angle = random.uniform(-1, 1)
        modified_img = modified_img.rotate(rotation_angle, expand=False)
        
        color_adjustments = [
            lambda img: ImageEnhance.Color(img).enhance(random.uniform(0.8, 1.2)),
            lambda img: ImageEnhance.Brightness(img).enhance(random.uniform(0.9, 1.1)),
            lambda img: ImageEnhance.Contrast(img).enhance(random.uniform(0.9, 1.1)),
            lambda img: adjust_hue(img, random.uniform(-0.1, 0.1)),
            lambda img: adjust_saturation(img, random.uniform(0.9, 1.1)),
            lambda img: adjust_rgb(img)
        ]
        
        for _ in range(random.randint(2, 4)):
            adjustment = random.choice(color_adjustments)
            modified_img = adjustment(modified_img)
        
        # Apply a random Instagram-like filter
        instagram_filters = [
            lambda img: apply_clarendon(img),
            lambda img: apply_gingham(img),
            lambda img: apply_moon(img),
            lambda img: apply_lark(img),
            lambda img: apply_reyes(img)
        ]
        
        random_instagram_filter = random.choice(instagram_filters)
        modified_img = random_instagram_filter(modified_img)
        
        modified_img.save(output_path, format='PNG')

def adjust_hue(img, amount):
    img = img.convert('HSV')
    h, s, v = img.split()
    h = h.point(lambda x: (x + int(amount * 255)) % 255)
    return Image.merge('HSV', (h, s, v)).convert('RGB')

def adjust_saturation(img, factor):
    img = img.convert('HSV')
    h, s, v = img.split()
    s = s.point(lambda x: int(x * factor))
    return Image.merge('HSV', (h, s, v)).convert('RGB')

def adjust_rgb(img):
    r, g, b = img.split()
    r = r.point(lambda i: i * random.uniform(0.9, 1.1))
    g = g.point(lambda i: i * random.uniform(0.9, 1.1))
    b = b.point(lambda i: i * random.uniform(0.9, 1.1))
    return Image.merge('RGB', (r, g, b))

# Instagram-like filters
def apply_clarendon(img):
    return ImageEnhance.Contrast(img).enhance(1.2)

def apply_gingham(img):
    sepia_filter = Image.new('RGB', img.size, (255, 240, 192))
    return Image.blend(img, sepia_filter, 0.13)

def apply_moon(img):
    return ImageOps.grayscale(img)

def apply_lark(img):
    r, g, b = img.split()
    r = r.point(lambda i: i * 1.1)
    b = b.point(lambda i: i * 0.9)
    return Image.merge('RGB', (r, g, b))

def apply_reyes(img):
    sepia_filter = Image.new('RGB', img.size, (239, 205, 173))
    return Image.blend(img, sepia_filter, 0.4)

def generate_random_filename(original_filename, length=10):
    _, ext = os.path.splitext(original_filename)
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    return f"{random_string}{ext}"

def create_unique_png_duplicate(input_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    unique_id = str(uuid.uuid4())
    
    random_filename = generate_random_filename(input_path)
    output_path = os.path.join(output_dir, random_filename)
    
    with Image.open(input_path) as img:
        metadata = PngInfo()
        metadata.add_text("UniqueID", unique_id)
        img.save(output_path, "PNG", pnginfo=metadata)

    end_date = datetime(2024, 1, 1).timestamp()
    start_date = datetime(2000, 1, 1).timestamp() 
    
    random_ctime = random.uniform(start_date, end_date)
    random_mtime = random.uniform(random_ctime, end_date)
    random_atime = random.uniform(random_mtime, end_date)
    
    os.utime(output_path, (random_atime, random_mtime))
    
    try:
        win32_setctime.setctime(output_path, random_ctime)
    except:
        print("Warning: Unable to set creation time. This might be due to non-Windows OS or missing permissions.")
    
    print(f"Creation time set to: {datetime.fromtimestamp(random_ctime)}")
    print(f"Modification time set to: {datetime.fromtimestamp(random_mtime)}")
    print(f"Access time set to: {datetime.fromtimestamp(random_atime)}")

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not os.path.exists('IMAGES'):
        os.makedirs('IMAGES')
    
    if update.message.photo:
        # Get the largest available photo size
        photo = update.message.photo[-1]
        
        # Check if we've already processed this image
        if 'processed_photos' not in context.user_data:
            context.user_data['processed_photos'] = set()
        
        if photo.file_unique_id in context.user_data['processed_photos']:
            return  # Skip this photo if we've already processed it
        
        context.user_data['processed_photos'].add(photo.file_unique_id)
        
        file = await context.bot.get_file(photo.file_id)
        file_extension = file.file_path.split('.')[-1]
        file_name = f"image_{context.user_data.get('image_count', 0) + 1}.{file_extension}"
        file_path = os.path.join('IMAGES', file_name)
        
        await file.download_to_drive(file_path)
        
        context.user_data['image_count'] = context.user_data.get('image_count', 0) + 1
        await update.message.reply_text(f"Image saved as {file_name}")
    else:
        await update.message.reply_text("Please send an image.")

    change_images()
    output_folder = "OUTPUT"

    if os.path.exists(output_folder):
        image_files = [f for f in os.listdir(output_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        if image_files:
            await update.message.reply_text("Sending processed images...")
            for image_file in image_files:
                image_path = os.path.join(output_folder, image_file)
                await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(image_path, 'rb'))
        else:
            await update.message.reply_text("No processed images found in the OUTPUT folder.")
    else:
        await update.message.reply_text("OUTPUT folder not found.")

    dsa = find_png_files("OUTPUT")
    for images in dsa:
        os.remove(f"OUTPUT/{images}")

    dsa = find_png_files("IMAGES")
    for images in dsa:
        os.remove(f"IMAGES/{images}")

def change_mp4_metadata_random(folder_path):
    fake = Faker()
    genres = ['Rock', 'Pop', 'Hip Hop', 'R&B', 'Country', 'Jazz', 'Classical', 'Electronic', 'Blues', 'Reggae']

    for filename in os.listdir(folder_path):
        if filename.endswith('.mp4'):
            file_path = os.path.join(folder_path, filename)
            
            # Generate random metadata
            new_metadata = {
                'title': fake.catch_phrase(),
                'artist': fake.name(),
                'album': fake.word().capitalize(),
                'year': str(random.randint(1950, 2024)),
                'comment': fake.sentence(),
                'genre': random.choice(genres),
                'creation_date': fake.date_time_between(start_date="-10y", end_date="now")
            }
            
            # Open the MP4 file
            audio = MP4(file_path)
            
            # Update metadata
            audio['\xa9nam'] = new_metadata['title']
            audio['\xa9ART'] = new_metadata['artist']
            audio['\xa9alb'] = new_metadata['album']
            audio['\xa9day'] = new_metadata['year']
            audio['\xa9cmt'] = new_metadata['comment']
            audio['\xa9gen'] = new_metadata['genre']
            
            # Save changes
            audio.save()
            
            # Update creation date
            os.utime(file_path, (new_metadata['creation_date'].timestamp(), new_metadata['creation_date'].timestamp()))
            
            print(f"Updated metadata for: {filename}")
            print(f"New metadata: {new_metadata}")

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

def duplicate_videos():

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
        duplicate_videos()
        folder_path = r'US'
        change_mp4_metadata_random(folder_path)
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

async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    questions = [
        "Please input how many random effects should be added (1-10), Choose small number for less variation",
        "Please input how many unicalizations should be done to the video (Number only) (How many videos to make)",
        "Please input minimum video length (Number only)",
        "Please input maximum video length (Number only)",
        "Enable mirroring? (1 - yes, 0 - no)",
        "Enable fade-in effect? (1 - yes, 0 - no)",
        "Enable rotation effect? (1 - yes, 0 - no)",
        "Enable blur? (1 - yes, 0 - no)",
        "Enable blur-in effect? (1 - yes, 0 - no)"
    ]
    
    context.user_data['settings'] = {}
    context.user_data['current_question'] = 0
    
    await ask_next_question(update, context)

async def ask_next_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    questions = [
        "Please input how many random effects should be added (1-10), Choose small number for less variation",
        "Please input how many unicalizations should be done to the video (Number only) (How many videos to make)",
        "Please input minimum video length (Number only)",
        "Please input maximum video length (Number only)",
        "Enable mirroring? (1 - yes, 0 - no)",
        "Enable fade-in effect? (1 - yes, 0 - no)",
        "Enable rotation effect? (1 - yes, 0 - no)",
        "Enable blur? (1 - yes, 0 - no)",
        "Enable blur-in effect? (1 - yes, 0 - no)"
    ]
    
    if context.user_data['current_question'] < len(questions):
        await update.message.reply_text(questions[context.user_data['current_question']])
    else:
        if context.user_data['settings'].get('doblur') or context.user_data['settings'].get('doBlurIn'):
            await update.message.reply_text("Input blur depth, in px, Number only.")
        else:
            await save_settings(update, context)

async def handle_settings_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current_question = context.user_data['current_question']
    answer = update.message.text
    
    settings_keys = ['rel', 'vidc', 'mind', 'maxd', 'doMirror', 'showEffect', 'doRotate', 'doblur', 'doBlurIn']
    
    if current_question < len(settings_keys):
        key = settings_keys[current_question]
        if current_question < 4:
            try:
                value = int(answer)
            except ValueError:
                await update.message.reply_text("Please enter a valid integer.")
                return
        else:  
            value = bool(int(answer))
        
        context.user_data['settings'][key] = value
        context.user_data['current_question'] += 1
        await ask_next_question(update, context)
    elif 'blursigma' not in context.user_data['settings']:
        try:
            context.user_data['settings']['blursigma'] = int(answer)
            await save_settings(update, context)
        except ValueError:
            await update.message.reply_text("Please enter a valid integer for blur depth.")

async def save_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    settings = context.user_data['settings']
    if not settings.get('doblur') and not settings.get('doBlurIn'):
        settings['blursigma'] = 0
    if 'blursigma' not in settings:
        settings['blursigma'] = 0

    with open('settings.json', 'w') as f:
        json.dump(settings, f)
    await update.message.reply_text('Settings successfully saved!')

async def img_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data['waiting_for_name'] = True
    await update.message.reply_text("How many duplicates of the images should be created?")

async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get('waiting_for_name'):
        name = update.message.text
        context.user_data['waiting_for_name'] = False
        with open('settings_image.txt', 'w') as file:
            file.write(name)
        await update.message.reply_text(f"Settings Saved!")
    else:
        await handle_settings_input(update, context)

async def handle_settings_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('waiting_for_name'):
        await handle_name(update, context)
        return

    current_question = context.user_data['current_question']
    answer = update.message.text

app = ApplicationBuilder().token("token here").build()
app.add_handler(CommandHandler("run", run))
app.add_handler(CommandHandler("done", done))
app.add_handler(CommandHandler("settings", settings))
app.add_handler(CommandHandler("img_settings", img_settings))
app.add_handler(MessageHandler(filters.VIDEO, handle_video))
app.add_handler(MessageHandler(filters.PHOTO, handle_image))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_settings_input))
app.run_polling()
