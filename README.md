# YOLO 数据集合并工具 / YOLO Dataset Merging Tool

## 简介 / Introduction

本工具用于将多个符合 YOLO 标注格式的数据集文件夹合并为一个统一的数据集。  
This tool is used to merge multiple YOLO-format dataset folders into a single unified dataset.

打包后的 EXE 程序无需安装 Python 环境，可直接在 Windows 系统上运行。  
The distributed EXE version does not require a Python environment and can be run directly on Windows.

---

## 目录结构要求 / Directory Structure Requirements

每个单独的数据集文件夹必须符合以下结构：  
Each individual dataset folder must follow the structure below:

DatasetA
├── images/
│    └── train/
│         ├── pic1.jpg
│         ├── pic2.jpg
│         └── …
└── labels/
     └── train/
          ├── label1.txt
          ├── label2.txt
          └── classes.txt


- **classes.txt**：每行一个类别名称，类别 ID 以文件中行序（从 0 开始）对应。  
  **classes.txt**: Each line contains a class name. The class IDs correspond to the line order (starting from 0).

- **标签文件 (.txt)**：格式为  类别ID x_center y_center width height
- **Label files (.txt)**: Format is  class_id x_center y_center width height

- 
---

## 使用方法 / How to Use

### 1. 准备工作 / Preparation

- **数据集要求 / Dataset Requirements**  
确保各个数据集文件夹中均包含 `images/train` 与 `labels/train` 文件夹，且 `labels/train` 中有 `classes.txt`。  
Ensure that each dataset folder contains `images/train` and `labels/train`, and that a `classes.txt` file exists in `labels/train`.

- **运行环境 / Environment**  
已打包为 EXE，无需安装 Python。  
The program is packaged as an EXE and does not require Python.

### 2. 运行程序 / Running the Program

1. **启动程序 / Launch the Program**  
 - 双击运行 EXE 文件（例如：`YOLO_Dataset_Merge.exe`）。  
   Double-click the EXE file (e.g., `YOLO_Dataset_Merge.exe`).

2. **选择数据集根目录 / Select the Root Directory of Datasets**  
 - 点击界面上的“选择文件夹”按钮，选择包含多个数据集文件夹的根目录。  
   Click the "Select Folder" button and choose the root directory that contains multiple dataset folders.

3. **选择输出目录 / Select the Output Directory**  
 - 点击另一个“选择文件夹”按钮，选择输出目录，该目录用于存放合并后的数据集。  
   Click the other "Select Folder" button and choose the output directory where the merged dataset will be stored.

4. **开始合并 / Start Merging**  
 - 点击“开始合并”按钮后，程序将自动遍历各数据集，合并类别，并复制图片及标签文件到输出目录。  
   After clicking the "Start Merging" button, the program will automatically traverse each dataset folder, merge the classes, and copy the image and label files to the output directory.

5. **查看日志 / Check the Log**  
 - 合并过程中的详细信息将在窗口下方的日志区域显示。  
   Detailed information about the merging process will be displayed in the log area at the bottom of the window.

6. **合并完成 / Merging Completed**  
 - 日志提示“所有数据集合并完成！输出目录：xxx”时，说明合并工作完成。  
   When the log displays "All datasets merged! Output directory: xxx", the merging process is complete.

---

## 输出目录结构 / Output Directory Structure

合并后的数据集将输出到指定的输出目录，其目录结构如下：

DatasetC
├── images/
│    └── train/
│         ├── pic1.jpg
│         ├── pic2.jpg
│         └── …
└── labels/
     └── train/
          ├── label1.txt
          ├── label2.txt
          └── classes.txt


- 程序会在复制文件时在原文件名前加上所属数据集文件夹名称前缀，避免文件名冲突。  
  The program renames the files by adding the dataset folder name as a prefix to avoid filename conflicts.

---

## 注意事项 / Important Notes

- **目录结构 / Directory Structure**  
  请确保每个数据集文件夹中存在 `images/train` 和 `labels/train/classes.txt`。否则，该数据集将被跳过，日志中会有提示。  
  Make sure that every dataset folder contains `images/train` and `labels/train/classes.txt`. Otherwise, that dataset will be skipped and a message will be shown in the log.

- **标签文件格式 / Label File Format**  
  标签文件中的类别 ID 必须为数字且从 0 开始。  
  The class IDs in the label files must be numeric and start from 0.

- **空标签文件 / Empty Label Files**  
  如果某个标签文件为空（表示图片没有标注），程序会生成对应的空文件，确保图片和标签文件一一对应。  
  If a label file is empty (indicating that the image has no annotations), the program will create a corresponding empty file to ensure that images and label files correspond correctly.

- **类别合并逻辑 / Class Merging Logic**  
  程序以最先处理的数据集为基准建立全局类别列表。如果后续数据集中存在相同类别，则映射为同一全局 ID；如有新类别，则追加到全局列表中。请核对合并后的 `classes.txt`。  
  The program builds the global class list based on the dataset processed first. If subsequent datasets contain the same class, they will be mapped to the same global ID; new classes will be appended to the global list. Please verify the merged `classes.txt` file.

- **文件重命名 / File Renaming**  
  为防止不同数据集中存在同名文件，程序会在复制的图片和标签文件名前添加数据集文件夹名称作为前缀。  
  To avoid filename conflicts across datasets, the program will add the dataset folder name as a prefix to the copied image and label files.

- **日志 / Log**  
  请留意程序界面下方的日志输出，如果有错误或异常提示，请根据日志信息检查相应的数据集结构和文件格式。  
  Please pay attention to the log output at the bottom of the interface. If errors or exceptions occur, check the respective dataset structure and file formats based on the log information.

---

## 问题排查 / Troubleshooting

- **未显示其他数据集信息 / Missing Dataset Information**  
  请检查输入根目录下是否存在多个符合要求的数据集文件夹。  
  Ensure that there are multiple dataset folders that meet the requirements under the input root directory.

- **标签文件更新不正确 / Incorrect Label Updates**  
  检查各数据集的 `classes.txt` 文件内容是否正确，以及标签文件中第一项是否为数字且从 0 开始。  
  Verify that the `classes.txt` content in each dataset folder is correct and that the first item in the label files is a number starting from 0.

- **程序报错或异常 / Errors or Exceptions**  
  请查看日志窗口中的详细错误信息，根据提示检查数据集文件夹结构或文件格式。  
  Please check the detailed error messages in the log window and verify the dataset folder structure or file formats accordingly.

---

通过以上说明，你可以顺利使用本工具将多个 YOLO 数据集合并为一个统一的数据集。  
With the above instructions, you can successfully merge multiple YOLO datasets into a single unified dataset.

如有问题或建议，欢迎反馈！  
If you have any questions or suggestions, please feel free to provide feedback!


