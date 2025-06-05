#!/usr/bin/env python3
"""
PyConcatenator - 画像連結CLIツール
ゲームアセット制作向けの画像連結ユーティリティ
"""

import os
import glob
import datetime
import subprocess
import platform
import random
from pathlib import Path
from PIL import Image


def find_image_folders():
    """画像ファイルが含まれているフォルダを探索"""
    image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.bmp', '*.gif', '*.tiff']
    folders_with_images = set()
    
    # 現在のディレクトリとその下のフォルダを探索
    for root, dirs, files in os.walk('.'):
        # concatenatedフォルダは除外
        if 'concatenated' in root:
            continue
            
        for ext in image_extensions:
            if glob.glob(os.path.join(root, ext)):
                folders_with_images.add(root)
                break
    
    return sorted(list(folders_with_images))


def find_segment_files(folder_path):
    """指定フォルダ内のsegment_*.pngファイルを探索"""
    pattern = os.path.join(folder_path, 'segment_*.png')
    files = glob.glob(pattern)
    return sorted(files)


def check_image_sizes(file_paths):
    """画像ファイルのキャンバスサイズをチェック"""
    if not file_paths:
        return False, None
    
    try:
        # 最初の画像のサイズを基準とする
        with Image.open(file_paths[0]) as img:
            base_size = img.size
        
        # 他の画像のサイズと比較
        for file_path in file_paths[1:]:
            with Image.open(file_path) as img:
                if img.size != base_size:
                    return False, None
        
        return True, base_size
    except Exception as e:
        print(f"画像サイズチェック中にエラーが発生しました: {e}")
        return False, None


def concatenate_images(file_paths, direction, output_path):
    """画像を連結"""
    if not file_paths:
        return False
    
    try:
        images = []
        for file_path in file_paths:
            img = Image.open(file_path)
            images.append(img)
        
        # 連結方向に応じてキャンバスサイズを計算
        width, height = images[0].size
        
        if direction == 'horizontal':
            # 横連結
            total_width = width * len(images)
            total_height = height
            result_img = Image.new('RGBA', (total_width, total_height))
            
            x_offset = 0
            for img in images:
                result_img.paste(img, (x_offset, 0))
                x_offset += width
        else:
            # 縦連結
            total_width = width
            total_height = height * len(images)
            result_img = Image.new('RGBA', (total_width, total_height))
            
            y_offset = 0
            for img in images:
                result_img.paste(img, (0, y_offset))
                y_offset += height
        
        # 画像を保存
        result_img.save(output_path, 'PNG')
        
        # 開いた画像を閉じる
        for img in images:
            img.close()
        
        return True
    except Exception as e:
        print(f"画像連結中にエラーが発生しました: {e}")
        return False


def open_file_explorer(file_path):
    """ファイルエクスプローラーでファイルを開く"""
    try:
        system = platform.system()
        if system == 'Windows':
            subprocess.run(['explorer', '/select,', file_path])
        elif system == 'Darwin':  # macOS
            subprocess.run(['open', '-R', file_path])
        else:  # Linux
            subprocess.run(['xdg-open', os.path.dirname(file_path)])
    except Exception as e:
        print(f"ファイルエクスプローラーを開く際にエラーが発生しました: {e}")


def main():
    print("=== PyConcatenator - 画像連結CLIツール ===")
    print("ゲームアセット制作向け画像連結ユーティリティ\n")
    
    # Step 1: 画像フォルダを探索
    print("画像ファイルが含まれているフォルダを探索しています...")
    image_folders = find_image_folders()
    
    if not image_folders:
        print("画像ファイルが含まれているフォルダが見つかりませんでした。")
        return
    
    print("以下のフォルダが見つかりました:")
    for i, folder in enumerate(image_folders, 1):
        print(f"{i}. {folder}")
    print("(concatenatedフォルダは表示されません)")        
    
    # Step 2: フォルダ選択
    while True:
        try:
            folder_input = input("\nフォルダ名を入力してください（パス形式で入力可能）: ").strip()
            
            # 番号による選択もサポート
            if folder_input.isdigit():
                folder_index = int(folder_input) - 1
                if 0 <= folder_index < len(image_folders):
                    selected_folder = image_folders[folder_index]
                    break
                else:
                    print("無効な番号です。")
                    continue
            
            # パス形式での入力をチェック
            if os.path.exists(folder_input):
                selected_folder = folder_input
                break
            else:
                print("指定されたフォルダが見つかりません。")
                continue
        except ValueError:
            print("有効なフォルダ名または番号を入力してください。")
    
    # Step 3: segment_*.pngファイルを探索
    print(f"\n'{selected_folder}'フォルダ内のsegment_*.pngファイルを探索しています...")
    segment_files = find_segment_files(selected_folder)
    
    if not segment_files:
        print("segment_*.pngファイルが見つかりませんでした。")
        return
    
    print(f"{len(segment_files)}個のsegment_*.pngファイルが見つかりました:")
    for file_path in segment_files:
        print(f"  - {os.path.basename(file_path)}")
    
    # Step 4: 画像サイズチェック
    print("\n画像のキャンバスサイズをチェックしています...")
    sizes_match, base_size = check_image_sizes(segment_files)
    
    if not sizes_match:
        print("画像のキャンバスサイズがファイルごとに異なるため、正常に画像を連結できません。")
        return
    
    print(f"すべての画像のサイズが一致しています: {base_size[0]}x{base_size[1]}")
    
    # Step 5: 連結方向を選択
    while True:
        direction_input = input("\n連結方向を選択してください (1: 縦連結, 2: 横連結): ").strip()
        if direction_input == '1':
            direction = 'vertical'
            direction_text = '縦'
            break
        elif direction_input == '2':
            direction = 'horizontal'
            direction_text = '横'
            break
        else:
            print("1または2を入力してください。")
    
    # Step 6: 出力準備
    output_dir = Path('concatenated')
    output_dir.mkdir(exist_ok=True)
    
    # 現在時刻でファイル名を生成（秒＋3桁乱数）
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    random_suffix = random.randint(100, 999)
    output_filename = f"{timestamp}_{random_suffix}.png"
    output_path = output_dir / output_filename
    
    # Step 7: 連結実行
    print(f"\n{direction_text}方向に画像を連結しています...")
    success = concatenate_images(segment_files, direction, str(output_path))
    
    if not success:
        print("画像の連結に失敗しました。")
        return
    
    print(f"連結が完了しました。")
    print(f"出力ファイル: {output_path}")
    
    # Step 8: ファイルエクスプローラーで開くか確認
    while True:
        open_explorer = input("\nファイルをエクスプローラーで開きますか？ (y/n): ").strip().lower()
        if open_explorer in ['y', 'yes']:
            open_file_explorer(str(output_path))
            break
        elif open_explorer in ['n', 'no']:
            break
        else:
            print("yまたはnを入力してください。")
    
    print("\n処理が完了しました。")


if __name__ == "__main__":
    main()