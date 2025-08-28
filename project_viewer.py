#!/usr/bin/env python3
"""
Simple Project Viewer for LLM-Autonomous Engineer
View and browse generated projects
"""

import os
import sys
from pathlib import Path
import json

def list_projects():
    """List all available projects"""
    projects_dir = Path("generated_projects")
    if not projects_dir.exists():
        print("❌ No projects directory found")
        return []
    
    projects = []
    for project_path in projects_dir.iterdir():
        if project_path.is_dir() and project_path.name != "__pycache__":
            files = list(project_path.rglob("*"))
            file_count = len([f for f in files if f.is_file()])
            projects.append({
                "name": project_path.name,
                "path": str(project_path),
                "files": file_count
            })
    
    return projects

def view_project_files(project_name):
    """View files in a specific project"""
    project_path = Path(f"generated_projects/{project_name}")
    
    if not project_path.exists():
        print(f"❌ Project '{project_name}' not found")
        return
    
    print(f"\n📁 Project: {project_name}")
    print("=" * 50)
    
    files = []
    for file_path in project_path.rglob("*"):
        if file_path.is_file():
            relative_path = file_path.relative_to(project_path)
            size = file_path.stat().st_size
            files.append({
                "path": str(relative_path),
                "size": size,
                "full_path": str(file_path)
            })
    
    # Sort files by path
    files.sort(key=lambda x: x["path"])
    
    for i, file_info in enumerate(files, 1):
        print(f"{i:2d}. {file_info['path']} ({file_info['size']} bytes)")
    
    return files

def view_file_content(file_path):
    """View content of a specific file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"\n📄 File: {Path(file_path).name}")
        print("=" * 50)
        print(content)
        print("=" * 50)
        
    except UnicodeDecodeError:
        print(f"❌ Cannot display binary file: {file_path}")
    except Exception as e:
        print(f"❌ Error reading file: {e}")

def main():
    """Main interactive project viewer"""
    print("🤖 LLM-Autonomous Engineer - Project Viewer")
    print("=" * 50)
    
    while True:
        print("\nAvailable commands:")
        print("1. List all projects")
        print("2. View project files")
        print("3. View file content")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            projects = list_projects()
            if projects:
                print(f"\n📂 Found {len(projects)} projects:")
                for i, project in enumerate(projects, 1):
                    print(f"{i:2d}. {project['name']} ({project['files']} files)")
            else:
                print("❌ No projects found")
        
        elif choice == "2":
            project_name = input("Enter project name: ").strip()
            if project_name:
                files = view_project_files(project_name)
                if files:
                    file_choice = input("\nEnter file number to view (or press Enter to continue): ").strip()
                    if file_choice.isdigit():
                        file_idx = int(file_choice) - 1
                        if 0 <= file_idx < len(files):
                            view_file_content(files[file_idx]["full_path"])
        
        elif choice == "3":
            file_path = input("Enter full file path: ").strip()
            if file_path and Path(file_path).exists():
                view_file_content(file_path)
            else:
                print("❌ File not found")
        
        elif choice == "4":
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please enter 1-4.")

if __name__ == "__main__":
    main()
