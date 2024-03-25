rd /s /q "dist\"
mkdir .\dist\
pyinstaller --hidden-import fastparquet -p src/ --onedir -y -n ev-flex-metric src/ev_flex_metric/shifted_energy_profiles.py
copy README.md .\dist\
Xcopy /E .\package_files\* .\dist\
