import tkinter as tk
from tkinter import ttk, messagebox
import threading
import api_client
import secrets
import statify


class StatifyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Statify - Spotify Artist Analyzer")
        self.root.geometry("600x500")
        self.root.configure(bg="#1DB954")  # Spotify green
        
        # Initialize API client
        self.spotify_client = api_client.SpotifyAPI(secrets.client_id, secrets.client_secret)
        
        # Initialize metric calculators
        self.pmm = statify.potty_mouth_meter(self.spotify_client)
        self.mimim = statify.mom_i_made_it_meter(self.spotify_client)
        self.bff = statify.bff_picker(self.spotify_client)
        
        self.setup_ui()
    
    def setup_ui(self):
        # Title
        title_label = tk.Label(
            self.root, 
            text="STATIFY", 
            font=("Arial", 24, "bold"), 
            fg="white", 
            bg="#1DB954"
        )
        title_label.pack(pady=20)
        
        subtitle_label = tk.Label(
            self.root, 
            text="Spotify Artist Analyzer", 
            font=("Arial", 12), 
            fg="white", 
            bg="#1DB954"
        )
        subtitle_label.pack(pady=(0, 30))
        
        # Search frame
        search_frame = tk.Frame(self.root, bg="#1DB954")
        search_frame.pack(pady=20)
        
        search_label = tk.Label(
            search_frame, 
            text="Enter Artist Name:", 
            font=("Arial", 12), 
            fg="white", 
            bg="#1DB954"
        )
        search_label.pack()
        
        self.artist_entry = tk.Entry(
            search_frame, 
            font=("Arial", 12), 
            width=30,
            justify="center"
        )
        self.artist_entry.pack(pady=10)
        self.artist_entry.bind("<Return>", lambda event: self.analyze_artist())
        
        self.analyze_button = tk.Button(
            search_frame,
            text="Analyze Artist",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#1DB954",
            command=self.analyze_artist,
            width=20,
            height=2
        )
        self.analyze_button.pack(pady=10)
        
        # Loading label
        self.loading_label = tk.Label(
            self.root,
            text="",
            font=("Arial", 10),
            fg="white",
            bg="#1DB954"
        )
        self.loading_label.pack(pady=10)
        
        # Results frame
        self.results_frame = tk.Frame(self.root, bg="white", relief="raised", bd=2)
        self.results_frame.pack(pady=20, padx=40, fill="both", expand=True)
        
        # Initially hide results frame
        self.results_frame.pack_forget()
        
    def show_loading(self, show=True):
        if show:
            self.loading_label.config(text="Analyzing artist... Please wait...")
            self.analyze_button.config(state="disabled", text="Analyzing...")
        else:
            self.loading_label.config(text="")
            self.analyze_button.config(state="normal", text="Analyze Artist")
    
    def analyze_artist(self):
        artist_name = self.artist_entry.get().strip()
        if not artist_name:
            messagebox.showerror("Error", "Please enter an artist name")
            return
        
        # Run analysis in a separate thread to prevent UI freezing
        def run_analysis():
            try:
                self.show_loading(True)
                
                # Search for artist
                search_results = self.spotify_client.search_artists(query=artist_name, limit=1)
                artists = search_results.get("artists", {}).get("items", [])
                
                if not artists:
                    self.root.after(0, lambda: messagebox.showerror("Error", f"No artist found for '{artist_name}'"))
                    return
                
                artist = artists[0]
                artist_id = artist["id"]
                found_artist_name = artist["name"]
                
                # Calculate metrics
                pmm_score = self.pmm.calculate_pmm(artist_id)
                mimim_score = self.mimim.calculate_mimim(artist_id)
                bff_result = self.bff.find_bff(artist_id)
                
                # Update UI on main thread
                self.root.after(0, lambda: self.display_results(found_artist_name, pmm_score, mimim_score, bff_result))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
            finally:
                self.root.after(0, lambda: self.show_loading(False))
        
        # Start analysis in background thread
        thread = threading.Thread(target=run_analysis)
        thread.daemon = True
        thread.start()
    
    def display_results(self, artist_name, pmm_score, mimim_score, bff_result):
        # Clear previous results
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        # Artist name
        artist_label = tk.Label(
            self.results_frame,
            text=f"{artist_name}'s Statify Profile",
            font=("Arial", 16, "bold"),
            bg="white",
            fg="#1DB954"
        )
        artist_label.pack(pady=20)
        
        # PMM Score
        pmm_frame = tk.Frame(self.results_frame, bg="white")
        pmm_frame.pack(pady=10, padx=20, fill="x")
        
        tk.Label(
            pmm_frame,
            text="🤬 Potty Mouth Meter:",
            font=("Arial", 12, "bold"),
            bg="white",
            anchor="w"
        ).pack(side="left")
        
        tk.Label(
            pmm_frame,
            text=f"{pmm_score:.1f}%",
            font=("Arial", 12),
            bg="white",
            fg="#e22134",
            anchor="e"
        ).pack(side="right")
        
        # MIMIM Score
        mimim_frame = tk.Frame(self.results_frame, bg="white")
        mimim_frame.pack(pady=10, padx=20, fill="x")
        
        tk.Label(
            mimim_frame,
            text="👑 Mom-I-Made-It Meter:",
            font=("Arial", 12, "bold"),
            bg="white",
            anchor="w"
        ).pack(side="left")
        
        tk.Label(
            mimim_frame,
            text=f"{mimim_score['mimim_score']:.1f}/100",
            font=("Arial", 12),
            bg="white",
            fg="#1DB954",
            anchor="e"
        ).pack(side="right")
        
        # MIMIM details
        details_frame = tk.Frame(self.results_frame, bg="white")
        details_frame.pack(pady=(0, 10), padx=40, fill="x")
        
        tk.Label(
            details_frame,
            text=f"Popularity: {mimim_score['popularity']}/100 | Followers: {mimim_score['followers']:,}",
            font=("Arial", 10),
            bg="white",
            fg="gray"
        ).pack()
        
        # BFF
        bff_frame = tk.Frame(self.results_frame, bg="white")
        bff_frame.pack(pady=10, padx=20, fill="x")
        
        tk.Label(
            bff_frame,
            text="👯 BFF (Best Friend Forever):",
            font=("Arial", 12, "bold"),
            bg="white",
            anchor="w"
        ).pack(side="left")
        
        bff_text = "No collaborations found"
        if bff_result:
            bff_text = f"{bff_result['name']} ({bff_result['collaboration_count']} collabs)"
        
        tk.Label(
            bff_frame,
            text=bff_text,
            font=("Arial", 12),
            bg="white",
            fg="#1DB954",
            anchor="e"
        ).pack(side="right")
        
        # Show results frame
        self.results_frame.pack(pady=20, padx=40, fill="both", expand=True)
        
        # Clear search field
        self.artist_entry.delete(0, tk.END)


def main():
    root = tk.Tk()
    app = StatifyGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()