from flask import Flask, send_file
import threading
import time
from datetime import datetime
import os

app = Flask(__name__)

# Global variable to track if the update thread is running
update_thread_running = False

def update_news_periodically():
    while True:
        try:
            print("Starting update...")
            current_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            
            # Create a simple HTML file for testing
            with open('news.html', 'w', encoding='utf-8') as f:
                f.write(f'''
                <html>
                <head>
                    <meta charset="utf-8">
                    <title>News Feed</title>
                </head>
                <body>
                    <h1>Last Update: {current_time}</h1>
                    <p>Server is running!</p>
                </body>
                </html>
                ''')
            
            print(f"Update completed at {current_time}")
            time.sleep(30)
            
        except Exception as e:
            print(f"Error in update: {str(e)}")
            time.sleep(5)

def start_update_thread():
    global update_thread_running
    if not update_thread_running:
        thread = threading.Thread(target=update_news_periodically)
        thread.daemon = True
        thread.start()
        update_thread_running = True
        print("Background thread started")

@app.route('/')
def serve_news():
    try:
        # Create initial file if it doesn't exist
        if not os.path.exists('news.html'):
            with open('news.html', 'w', encoding='utf-8') as f:
                f.write('<html><body><h1>Initializing...</h1></body></html>')
        
        # Start update thread if not running
        start_update_thread()
        
        return send_file('news.html')
    except Exception as e:
        error_message = f"Error: {str(e)}"
        print(error_message)
        return error_message, 500

@app.route('/health')
def health_check():
    return {"status": "healthy", "time": str(datetime.now())}

# Initialize the app
print("Application starting...")
if not os.path.exists('news.html'):
    with open('news.html', 'w', encoding='utf-8') as f:
        f.write('<html><body><h1>Initializing...</h1></body></html>')
print("Initial news.html created")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)