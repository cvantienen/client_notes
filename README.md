# Starting Container 
'''bash
docker run -d --restart always -p 6969:6969 -v $(pwd):/app clientnotes
'''
Option B: With tmux or screen (Recommended for Monitoring)
'''bash
tmux new -s update_list
'''
python3 updateList.py
Press Ctrl+b then d to detach

'''bash
tmux attach -t update_list
'''✔️ 
This is safer and gives you easy access to the live output.
