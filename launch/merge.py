import os
import shutil
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import traceback

def load_classes(classes_path):
    """读取 classes.txt 文件，返回类别列表
    Read classes.txt file and return a list of classes
    """
    if not os.path.exists(classes_path):
        return []
    with open(classes_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def process_dataset(dataset_dir, global_classes, log_callback=None):
    """
    处理单个数据集文件夹：
      - 读取该数据集的 classes.txt，
      - 根据 global_classes（全局合并的类别列表）建立映射字典：{原id: 全局id}，
      - 如果当前数据集有新的类别，则追加到 global_classes 中。
    返回映射字典 mapping。

    Process a single dataset folder:
      - Read the classes.txt of the dataset,
      - Create a mapping dictionary based on global_classes (global merged class list): {original_id: global_id},
      - If the current dataset has new classes, append them to global_classes.
    Return the mapping dictionary.
    """
    dataset_name = os.path.basename(dataset_dir)
    classes_path = os.path.join(dataset_dir, "labels", "train", "classes.txt")
    dataset_classes = load_classes(classes_path)
    mapping = {}
    for i, cls in enumerate(dataset_classes):  # 原 id 从 0 开始 / Original id starts from 0
        orig_id = i
        if cls in global_classes:
            new_id = global_classes.index(cls)
        else:
            new_id = len(global_classes)
            global_classes.append(cls)
        mapping[orig_id] = new_id
    if log_callback:
        log_callback(f"[{dataset_name}] 类别映射 / Class mapping: {mapping}")
    return mapping

def update_label_file(src, dst, mapping, log_callback=None):
    """
    更新标签文件：
      - 对于非空文件，读取每一行，将第一项（类别 id）替换为 mapping 中对应的全局 id，
      - 对于空文件，直接复制为空文件。
    写入更新后的内容到 dst。

    Update label file:
      - For non-empty files, read each line and replace the first item (class id) with the corresponding global id in mapping,
      - For empty files, copy as an empty file.
    Write the updated content to dst.
    """
    # 如果文件为空，则生成一个空文件 / If the file is empty, generate an empty file
    if os.path.getsize(src) == 0:
        open(dst, 'w', encoding='utf-8').close()
        if log_callback:
            log_callback(f"标签文件 {src} 为空，生成空文件 / Label file {src} is empty, generating empty file.")
        return
    
    updated_lines = []
    with open(src, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            try:
                orig_id = int(parts[0])
                new_id = mapping.get(orig_id, orig_id)
            except Exception:
                new_id = parts[0]
            updated_line = " ".join([str(new_id)] + parts[1:])
            updated_lines.append(updated_line)
    with open(dst, 'w', encoding='utf-8') as f:
        for line in updated_lines:
            f.write(line + "\n")

def merge_datasets(input_root, output_root, log_callback=None):
    """
    遍历 input_root 下所有数据集文件夹（要求目录中同时存在 images/train 和 labels/train/classes.txt），
    对每个数据集：
      1. 读取其 classes.txt，并计算原id到全局id的映射（更新 global_classes），
      2. 复制图片文件到 output_root/images/train，重命名为 "数据集名_原文件名"，
      3. 复制并更新标签文件（除 classes.txt 外）到 output_root/labels/train，同样重命名。
    最后，将全局合并后的 classes.txt 写入 output_root/labels/train/classes.txt。

    Traverse all dataset folders under input_root (requires both images/train and labels/train/classes.txt in the directory),
    For each dataset:
      1. Read its classes.txt and calculate the mapping from original id to global id (update global_classes),
      2. Copy image files to output_root/images/train, renamed as "datasetname_originalfilename",
      3. Copy and update label files (except classes.txt) to output_root/labels/train, similarly renamed.
    Finally, write the globally merged classes.txt to output_root/labels/train/classes.txt.
    """
    images_out = os.path.join(output_root, "images", "train")
    labels_out = os.path.join(output_root, "labels", "train")
    os.makedirs(images_out, exist_ok=True)
    os.makedirs(labels_out, exist_ok=True)
    
    global_classes = []  # 全局合并后的类别列表 / Globally merged class list

    # 获取 input_root 下所有子文件夹（每个子文件夹为一个数据集） / Get all subfolders under input_root (each subfolder is a dataset)
    dataset_dirs = [os.path.join(input_root, d) for d in os.listdir(input_root) 
                    if os.path.isdir(os.path.join(input_root, d))]
    if log_callback:
        log_callback(f"共找到 {len(dataset_dirs)} 个数据集文件夹 / Found {len(dataset_dirs)} dataset folders.")
    
    for dataset_dir in dataset_dirs:
        dataset_name = os.path.basename(dataset_dir)
        images_dir = os.path.join(dataset_dir, "images", "train")
        labels_dir = os.path.join(dataset_dir, "labels", "train")
        classes_path = os.path.join(labels_dir, "classes.txt")
        
        # 检查是否符合要求 / Check if the requirements are met
        if not (os.path.exists(images_dir) and os.path.exists(labels_dir) and os.path.exists(classes_path)):
            if log_callback:
                log_callback(f"跳过 {dataset_name}：目录结构不完整 / Skip {dataset_name}: Incomplete directory structure.")
            continue

        # 处理当前数据集，获取类别 id 映射 / Process the current dataset and get the class id mapping
        mapping = process_dataset(dataset_dir, global_classes, log_callback)
        
        # 复制图片文件，重命名为 "数据集名_原文件名" / Copy image files, renamed as "datasetname_originalfilename"
        for filename in os.listdir(images_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                src_img = os.path.join(images_dir, filename)
                dst_img = os.path.join(images_out, f"{dataset_name}_{filename}")
                shutil.copy2(src_img, dst_img)
        
        # 处理标签文件：更新类别 id（跳过 classes.txt） / Process label files: update class id (skip classes.txt)
        for filename in os.listdir(labels_dir):
            if filename.lower() == "classes.txt":
                continue
            if filename.lower().endswith('.txt'):
                src_label = os.path.join(labels_dir, filename)
                dst_label = os.path.join(labels_out, f"{dataset_name}_{filename}")
                update_label_file(src_label, dst_label, mapping, log_callback)
                
        if log_callback:
            log_callback(f"数据集 {dataset_name} 处理完成 / Dataset {dataset_name} processed.")
    
    # 写入合并后的全局 classes.txt / Write the globally merged classes.txt
    classes_out_path = os.path.join(labels_out, "classes.txt")
    with open(classes_out_path, 'w', encoding='utf-8') as f:
        for cls in global_classes:
            f.write(cls + "\n")
    if log_callback:
        log_callback("合并后的 classes.txt 写入成功 / Merged classes.txt written successfully.")
        log_callback("所有数据集合并完成！输出目录 / All datasets merged! Output directory: " + output_root)

# -------------- GUI 部分 / GUI Section --------------
def select_input_folder():
    folder = filedialog.askdirectory(title="选择包含多个数据集文件夹的根目录 / Select the root directory containing multiple dataset folders")
    if folder:
        input_entry.delete(0, tk.END)
        input_entry.insert(0, folder)

def select_output_folder():
    folder = filedialog.askdirectory(title="选择输出文件夹 / Select the output folder")
    if folder:
        output_entry.delete(0, tk.END)
        output_entry.insert(0, folder)

def update_log(msg):
    log_text.insert(tk.END, msg + "\n")
    log_text.see(tk.END)

def start_merging():
    input_root = input_entry.get().strip()
    output_root = output_entry.get().strip()
    if not input_root:
        messagebox.showerror("错误 / Error", "请选择数据集根目录 / Please select the dataset root directory")
        return
    if not output_root:
        messagebox.showerror("错误 / Error", "请选择输出文件夹 / Please select the output folder")
        return
    start_button.config(state=tk.DISABLED)
    update_log("开始合并数据集... / Starting dataset merging...")
    
    def run():
        try:
            merge_datasets(input_root, output_root, log_callback=update_log)
        except Exception as e:
            update_log("错误 / Error: " + str(e))
            update_log(traceback.format_exc())
            messagebox.showerror("错误 / Error", str(e))
        finally:
            start_button.config(state=tk.NORMAL)
    
    threading.Thread(target=run, daemon=True).start()

# 创建 GUI 窗口 / Create GUI window
root = tk.Tk()
root.title("YOLO 数据集合并工具 / YOLO Dataset Merging Tool")

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

# 输入根目录 / Input root directory
input_label = tk.Label(frame, text="数据集根目录 / Dataset Root Directory:")
input_label.grid(row=0, column=0, sticky="e", padx=5, pady=5)
input_entry = tk.Entry(frame, width=50)
input_entry.grid(row=0, column=1, padx=5, pady=5)
input_button = tk.Button(frame, text="选择文件夹 / Select Folder", command=select_input_folder)
input_button.grid(row=0, column=2, padx=5, pady=5)

# 输出文件夹 / Output folder
output_label = tk.Label(frame, text="输出文件夹 / Output Folder:")
output_label.grid(row=1, column=0, sticky="e", padx=5, pady=5)
output_entry = tk.Entry(frame, width=50)
output_entry.grid(row=1, column=1, padx=5, pady=5)
output_button = tk.Button(frame, text="选择文件夹 / Select Folder", command=select_output_folder)
output_button.grid(row=1, column=2, padx=5, pady=5)

# 开始合并按钮 / Start merging button
start_button = tk.Button(frame, text="开始合并 / Start Merging", command=start_merging)
start_button.grid(row=2, column=1, pady=10)

# 日志输出区域 / Log output area
log_text = tk.Text(root, height=15, width=70)
log_text.pack(padx=10, pady=10)

root.mainloop()