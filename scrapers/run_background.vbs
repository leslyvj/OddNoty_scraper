Set WshShell = CreateObject("WScript.Shell")
' Define constants: 0 for hidden, True to wait (optional)
WshShell.Run "cmd /c set PYTHONPATH=c:\Users\ragna\OneDrive\Desktop\OddNoty&& set PYTHONIOENCODING=utf-8&& pythonw c:\Users\ragna\OneDrive\Desktop\OddNoty\scrapers\interactive_bot.py", 0, False
