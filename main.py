import os
import shutil
import glob
import sys
import ffmpeg
from optimization.image_editor import ImageEditor
from optimization.arguments import get_arguments
from face_crop_plus.cropper import Cropper
from optimization.merge import merge_faces

def get_file_extension(directory, filename):
    file_patterns = [os.path.join(directory, f"{filename}.*"),
                     os.path.join(directory, "*.jpg"),
                     os.path.join(directory, "*.png"),
                     os.path.join(directory, "*.mp4")]
    for pattern in file_patterns:
        files = glob.glob(pattern)
        if files:
            print(f"Files found with pattern: {pattern}")
            return os.path.splitext(files[0])[1][1:]  # Remove the dot from the extension
    return None

if __name__ == "__main__":
    args = get_arguments()

    os.makedirs(os.path.join("./data/src", "aligned"), exist_ok=True)
    os.makedirs(os.path.join("./data/dst", "aligned"), exist_ok=True)
    os.makedirs(os.path.join("./data/dst", "preded"), exist_ok=True)
    os.makedirs(os.path.join("./data/dst", "merged"), exist_ok=True)
    os.makedirs("./data/debug", exist_ok=True)

    print("Checking source directory:")
    print(os.listdir('./data/src'))
    
    print("Checking destination directory:")
    print(os.listdir('./data/dst'))

    src_ext = get_file_extension("./data/src", "src")
    dst_ext = get_file_extension("./data/dst", "dst")

    print(f"Source Extension: {src_ext}")
    print(f"Destination Extension: {dst_ext}")

    if not src_ext:
        print("No src file found")
        sys.exit()

    if not dst_ext:
        print("No dst file found")
        sys.exit()

    if src_ext in ["jpg", "png"]:
        src_file_path = f"./data/src/src.{src_ext}"
        if os.path.isfile(src_file_path):
            # Copying to a different name to avoid SameFileError
            dest_file_path = f"./data/src/src_copied.{src_ext}"
            if src_file_path != dest_file_path:
                shutil.copy2(src_file_path, dest_file_path)
        else:
            print(f"Source file {src_file_path} does not exist")
            sys.exit()
    else:
        print("src can only be jpg or png")
        sys.exit()

    if dst_ext in ["jpg", "png"]:
        dst_file_path = f"./data/dst/dst.{dst_ext}"
        if os.path.isfile(dst_file_path):
            # Copying to a different name to verify if it's accessible
            shutil.copy2(dst_file_path, f"./data/dst/dst_copied.{dst_ext}")
        else:
            print(f"Destination file {dst_file_path} does not exist")
            sys.exit()
    elif dst_ext in ["mp4"]:
        if not args.no_extract:
            print("Extracting video frames...")
            job = ffmpeg.input(f"./data/dst/dst.{dst_ext}")
            kwargs = {'pix_fmt': 'rgb24'}
            job = job.output(f"./data/dst/%5d.png", **kwargs)
            try:
                job.run()
            except:
                print(f"ffmpeg fail, job commandline: {str(job.compile())}")
    else:
        print("dst can only be jpg, png, or mp4")
        sys.exit()

    if not args.merge_crop_only and not args.merge_only:
        print("Requested Crop")
        cropper = Cropper(face_factor=0.7, strategy="largest", output_size=args.crop_size)
        cropper.process_dir(input_dir="./data/src", output_dir=os.path.join("./data/src", "aligned"))
        if not args.no_extract:
            cropper.process_dir(input_dir="./data/dst", output_dir=os.path.join("./data/dst", "aligned"))

    if not args.merge_only:
        print("Requested Edit")
        image_editor = ImageEditor(args)
        image_editor.edit_image_by_prompt()

    print("Requested Merge")
    merged_image = merge_faces(args, dst_ext)




