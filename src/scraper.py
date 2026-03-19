import sys
import io

# Force UTF-8 stdout/stderr so printing scraped Unicode won't raise encoding errors
if sys.stdout and (sys.stdout.encoding is None or sys.stdout.encoding.lower() != 'utf-8-sig'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8-sig', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8-sig', errors='replace')

import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
import time
import random
import google.genai as genai
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading 
from datetime import datetime

class ArticleScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Web Article Scraper")
        self.root.geometry("900x700")
        
        # Variables
        self.api_key = tk.StringVar()
        self.urls_text = None
        self.output_file = tk.StringVar(value="news_results.csv")
        self.certificate_path = tk.StringVar(value=r"")
        self.is_running = False
        self.df = None

        self.client = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Create the user interface"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # API Key section
        row = 0
        ttk.Label(main_frame, text="Gemini API Key:", font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=5)
        api_entry = ttk.Entry(main_frame, textvariable=self.api_key, width=50, show="*")
        api_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # Certificate path section
        row += 1
        ttk.Label(main_frame, text="Certificate Path:", font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=5)
        cert_frame = ttk.Frame(main_frame)
        cert_frame.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        cert_frame.columnconfigure(0, weight=1)
        
        cert_entry = ttk.Entry(cert_frame, textvariable=self.certificate_path)
        cert_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(cert_frame, text="Browse", command=self.browse_certificate).grid(row=0, column=1)
        
        # Output file section
        row += 1
        ttk.Label(main_frame, text="Output CSV File:", font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=5)
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        output_frame.columnconfigure(0, weight=1)
        
        output_entry = ttk.Entry(output_frame, textvariable=self.output_file)
        output_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(output_frame, text="Browse", command=self.browse_output).grid(row=0, column=1)
        
        # URLs section
        row += 1
        ttk.Label(main_frame, text="URLs to Scrape (one per line):", font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        
        row += 1
        self.urls_text = scrolledtext.ScrolledText(main_frame, width=80, height=8, wrap=tk.WORD)
        self.urls_text.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        self.urls_text.insert(1.0, "https://www.sciencedirect.com/journal/agricultural-and-forest-meteorology/issues\n")
        
        # Buttons section
        row += 1
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="Start Scraping", command=self.start_scraping, style='Accent.TButton')
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_scraping, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=5)
        
        ttk.Button(button_frame, text="Clear Log", command=self.clear_log).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="Open CSV", command=self.open_csv).grid(row=0, column=3, padx=5)
        
        # Progress section
        row += 1
        ttk.Label(main_frame, text="Progress:", font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        
        row += 1
        self.progress = ttk.Progressbar(main_frame, mode='determinate')
        self.progress.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Status label
        row += 1
        self.status_label = ttk.Label(main_frame, text="Ready", foreground="blue")
        self.status_label.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Log section
        row += 1
        ttk.Label(main_frame, text="Log:", font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        
        row += 1
        self.log_text = scrolledtext.ScrolledText(main_frame, width=80, height=15, wrap=tk.WORD, state=tk.DISABLED)
        self.log_text.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Configure grid weights for resizing
        main_frame.rowconfigure(4, weight=1)  # URLs text
        main_frame.rowconfigure(10, weight=2)  # Log text
        
    def browse_certificate(self):
        """Browse for certificate file"""
        filename = filedialog.askopenfilename(
            title="Select Certificate File",
            filetypes=[("PEM files", "*.pem"), ("All files", "*.*")]
        )
        if filename:
            self.certificate_path.set(filename)
    
    def browse_output(self):
        """Browse for output CSV file"""
        filename = filedialog.asksaveasfilename(
            title="Select Output CSV File",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.output_file.set(filename)
    
    def log(self, message, level="INFO"):
        """Add message to log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {level}: {message}\n"
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, formatted_message)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        # Also print to console
        print(formatted_message.strip())
    
    def clear_log(self):
        """Clear the log"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def open_csv(self):
        """Open the output CSV file"""
        import os
        output_path = self.output_file.get()
        if os.path.exists(output_path):
            os.startfile(output_path)
        else:
            messagebox.showwarning("File Not Found", f"The file {output_path} does not exist yet.")
    
    def update_status(self, message, color="blue"):
        """Update status label"""
        self.status_label.config(text=message, foreground=color)
    
    def start_scraping(self):
        """Start the scraping process"""
        print("SCRAPING THREAD STARTED") 
        # Validate inputs
        if not self.api_key.get():
            messagebox.showerror("Error", "Please enter your Gemini API Key")
            return
        
        urls = self.urls_text.get(1.0, tk.END).strip().split('\n')
        urls = [url.strip() for url in urls if url.strip()]
        
        if not urls:
            messagebox.showerror("Error", "Please enter at least one URL")
            return
        
        # Disable start button, enable stop button
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.is_running = True
        
        # Clear log and reset progress
        self.clear_log()
        self.progress['value'] = 0
        self.progress['maximum'] = len(urls)
        
        # Start scraping in a separate thread
        thread = threading.Thread(target=self.scrape_articles, args=(urls,), daemon=True)
        thread.start()
    
    def stop_scraping(self):
        """Stop the scraping process"""
        self.is_running = False
        self.log("Stopping scraping process...", "WARNING")
        self.update_status("Stopped by user", "orange")
    
    def scrape_articles(self, urls):
        """Main scraping function (runs in separate thread)"""
        print("scrape articles started") 
        try:
            self.log(f"Starting scraping process for {len(urls)} URLs")
            self.update_status("Running...", "green")
            
            # Initialize Gemini client
            self.client = genai.Client(api_key=self.api_key.get())
            
            # Initialize or load existing DataFrame
            output_path = self.output_file.get()
            try:
                self.df = pd.read_csv(output_path)
                self.log(f"Loaded existing data: {len(self.df)} articles")
            except FileNotFoundError:
                self.df = pd.DataFrame(columns=['title', 'url', 'published_date', 'retrieved_on', 'source_url'])
                self.log("Starting with empty DataFrame")
            
            # Process each URL
            for i, url in enumerate(urls):
                if not self.is_running:
                    break
                
                self.log(f"\n{'='*60}")
                self.log(f"Processing {i+1}/{len(urls)}: {url}")
                self.log(f"{'='*60}")
                
                result = self.get_articles_from_url(url)
                
                if isinstance(result, pd.DataFrame) and not result.empty:
                    result['retrieved_on'] = pd.Timestamp.now()
                    result['source_url'] = url
                    
                    self.df = pd.concat([self.df, result], ignore_index=True)
                    self.df = self.df.drop_duplicates(subset=['url', 'title'], keep='first')
                    
                    self.df.to_csv(output_path, index=False, encoding = 'utf-8-sig')
                    self.log(f"✓ Added {len(result)} articles. Total: {len(self.df)}", "SUCCESS")
                else:
                    self.log(f"✗ No articles found for {url}", "WARNING")
                
                # Update progress
                self.progress['value'] = i + 1
                
                # Delay between requests
                if i < len(urls) - 1 and self.is_running:
                    delay = random.uniform(2, 5)
                    self.log(f"Waiting {delay:.1f} seconds before next request...")
                    time.sleep(delay)
            
            # Completion
            if self.is_running:
                self.log(f"\n{'='*60}")
                self.log("SCRAPING COMPLETE", "SUCCESS")
                self.log(f"{'='*60}")
                self.log(f"Total articles collected: {len(self.df)}")
                self.log(f"Results saved to: {output_path}")
                self.update_status("Complete!", "green")
                messagebox.showinfo("Success", f"Scraping complete! {len(self.df)} total articles collected.")
            
        except Exception as e:
            self.log(f"CRITICAL ERROR: {str(e)}", "ERROR")
            self.update_status("Error occurred", "red")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        
        finally:
            # Re-enable start button, disable stop button
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.is_running = False
    
    def get_relevant_html(self, url):
        """Extract only article/content sections from HTML"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
        }

        try:
            response = requests.get(
                url,
                headers=headers,
                verify=self.certificate_path.get(),
                timeout=30
            )
            self.log(f"HTTP Status: {response.status_code}")
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unwanted elements
            for element in soup.find_all(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe', 'noscript']):
                element.decompose()
            
            # Try to find main content container
            content_selectors = [
                'main', 'article', '[role="main"]', '.main-content', '#main-content',
                '.content', '#content', '.articles', '.article-list', '.publication-list',
                '.search-results', '.news-list', '.post-list', '.entry-content',
            ]
            
            content = None
            for selector in content_selectors:
                content = soup.select_one(selector)
                if content:
                    self.log(f"Found content using selector: {selector}")
                    break
            
            if not content:
                self.log("No specific content container found, using body")
                content = soup.body
                if content:
                    for noise in content.find_all(['nav', 'footer', 'header', 'aside']):
                        noise.decompose()
                    for noise in content.select('.sidebar, #sidebar, .advertisement, .ad, .social-share'):
                        noise.decompose()
            
            if content:
                html_str = str(content)
                self.log(f"Extracted HTML length: {len(html_str)} characters")
                return html_str
            else:
                self.log("Could not extract content", "ERROR")
                return None
                
        except requests.exceptions.RequestException as e:
            self.log(f"Error fetching URL: {e}", "ERROR")
            return None
    
    def gemini_find_articles(self, html):
        """Use Gemini to extract article information from HTML"""
        print('gemini_find_articles')
        max_chars = 50000
        if len(html) > max_chars:
            html = html[:max_chars]
            self.log(f"HTML truncated to {max_chars} characters", "WARNING")
        
        prompt = f"""Please give me a list of UP TO 30 articles or journal publications from the following HTML, 
        including their titles, full url, and publication dates. 
        
        The expected response format is a JSON object with a key 'articles', where each article is an object with:
        - 'title': the article title (string)
        - 'url': the article URL (string)
        - 'published_date': the publication date if available, otherwise null
        
        Only include complete article entries. Do not include partial entries.
        Ensure the JSON is properly closed with }} at the end.
        
        HTML: {html}"""
        
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    max_output_tokens=8192,
                    temperature=0.1,
                )
            )
            
            if hasattr(response, 'candidates') and response.candidates:
                finish_reason = response.candidates[0].finish_reason
                self.log(f"Gemini finish reason: {finish_reason}")
                if finish_reason == 'MAX_TOKENS':
                    self.log("Response truncated due to max tokens!", "WARNING")
            
            raw_output = response.text
            
            if raw_output is None:
                self.log("No output from Gemini API", "ERROR")
                return None
            
            clean_json = raw_output.strip()
            if clean_json.startswith('```json'):
                clean_json = clean_json.replace('```json', '').replace('```', '').strip()
            elif clean_json.startswith('```'):
                clean_json = clean_json.replace('```', '').strip()
            
            if not clean_json.endswith('}') and not clean_json.endswith(']'):
                self.log("JSON appears truncated, attempting to fix...", "WARNING")
                open_braces = clean_json.count('{') - clean_json.count('}')
                open_brackets = clean_json.count('[') - clean_json.count(']')
                clean_json += ']' * open_brackets + '}' * open_braces
                self.log(f"Added {open_brackets} ] and {open_braces} }}")
            
            self.log("JSON extraction successful")
            return clean_json
            
        except Exception as e:
            self.log(f"Error calling Gemini API: {e}", "ERROR")
            return None
    
    def get_articles_from_url(self, url):
        """Main function to extract articles from a URL"""
        cleaned_html = self.get_relevant_html(url)
        
        if cleaned_html is None:
            self.log(f"Failed to retrieve HTML", "ERROR")
            return None
        
        articles_json = self.gemini_find_articles(cleaned_html)

        
        if articles_json is None:
            self.log(f"Failed to get articles from Gemini", "ERROR")
            return None
        
        try:
            articles = json.loads(articles_json)
            
            if 'articles' not in articles:
                self.log(f"No 'articles' key found in response", "WARNING")
                self.log(f"Available keys: {list(articles.keys())}")
                return None
            
            if not articles['articles']:
                self.log(f"No articles found in JSON response", "WARNING")
                return None
            
            results = pd.DataFrame(articles['articles'])
            self.log(f"Successfully extracted {len(results)} articles", "SUCCESS")
            return results
            
        except json.JSONDecodeError as e:
            self.log(f"Error parsing JSON: {e}", "ERROR")
            self.log(f"First 500 chars: {articles_json[:500]}")
            return None
        except Exception as e:
            self.log(f"Unexpected error: {e}", "ERROR")
            return None

def main():
    root = tk.Tk()
    app = ArticleScraperGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

