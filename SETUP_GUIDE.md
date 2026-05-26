# Installation & Setup Guide

## Requirements
- Windows 10/11
- Python 3.11+
- Google Chrome

## 1. Clone Project
```powershell
git clone YOUR_REPO_URL
cd ai_reseller_suite_vision
```

## 2. Create Virtual Environment
```powershell
python -m venv venv
```

## 3. Activate
```powershell
.\venv\Scripts\activate
```

## 4. Install Dependencies
```powershell
pip install playwright pillow rembg onnxruntime opencv-python numpy
```

## 5. Install Playwright Browsers
```powershell
playwright install
```

## 6. Add Listing Photos
Example:

listing_images/
└── asian_dress/
    ├── 1.jpg
    ├── 2.jpg

## 7. Run Project
```powershell
python main.py
```

## Workflow
1. Chrome launches automatically
2. Photos processed
3. Background removed
4. Listing generated
5. Images uploaded
6. Category selected
7. Price discounted by 40%
8. Human review before posting

## Troubleshooting

### CDP Error
```powershell
taskkill /F /IM chrome.exe
python main.py
```

### Broken venv
```powershell
Remove-Item -Recurse -Force venv
python -m venv venv
```
