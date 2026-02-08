# AI Analysis Tab Implementation
# Add this section to emyuel_gui.py

def setup_ai_analysis_tab(self, parent):
    """Setup AI-driven autonomous security analysis tab"""
    
    # Main container with scroll
    canvas = tk.Canvas(parent, bg=self.colors['bg_primary'], highlightthickness=0)
    scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=self.colors['bg_primary'])
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # ===== Header Section =====
    header_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_secondary'], relief='flat', bd=2)
    header_frame.pack(fill='x', padx=20, pady=20)
    
    header_label = tk.Label(
        header_frame,
        text="🤖 AI-Driven Autonomous Security Analysis",
        font=('Segoe UI', 14, 'bold'),
        fg=self.colors['accent_cyan'],
        bg=self.colors['bg_secondary']
    )
    header_label.pack(anchor='w', padx=20, pady=15)
    
    desc_label = tk.Label(
        header_frame,
        text="AI will analyze the target, generate a custom testing strategy, and adapt based on results",
        font=('Segoe UI', 9),
        fg=self.colors['text_secondary'],
        bg=self.colors['bg_secondary']
    )
    desc_label.pack(anchor='w', padx=20, pady=(0, 15))
    
    # ===== Target URL Section =====
    url_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_secondary'], relief='flat', bd=2)
    url_frame.pack(fill='x', padx=20, pady=(0, 20))
    
    url_label = tk.Label(
        url_frame,
        text="🎯 Target URL",
        font=('Segoe UI', 11, 'bold'),
        fg=self.colors['text_primary'],
        bg=self.colors['bg_secondary']
    )
    url_label.pack(anchor='w', padx=20, pady=(15, 10))
    
    url_input_frame = tk.Frame(url_frame, bg=self.colors['bg_secondary'])
    url_input_frame.pack(fill='x', padx=20, pady=(0, 15))
    
    self.ai_target_var = tk.StringVar(value='https://example.com')
    
    url_entry = tk.Entry(
        url_input_frame,
        textvariable=self.ai_target_var,
        font=('Segoe UI', 10),
        bg=self.colors['bg_tertiary'],
        fg=self.colors['text_primary'],
        insertbackground=self.colors['text_primary'],
        relief='flat',
        bd=0
    )
    url_entry.pack(side='left', fill='x', expand=True, ipady=10, padx=(0, 10))
    
    # Start Analysis Button
    start_btn = tk.Button(
        url_input_frame,
        text="🚀 Start AI Analysis",
        font=('Segoe UI', 10, 'bold'),
        bg=self.colors['accent_cyan'],
        fg='#000000',
        activebackground=self.colors['accent_purple'],
        activeforeground='#ffffff',
        relief='flat',
        cursor='hand2',
        command=self.start_ai_analysis,
        padx=20,
        pady=10
    )
    start_btn.pack(side='right')
    
    #===== Step Progress Visualization =====
    progress_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_secondary'], relief='flat', bd=2)
    progress_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
    
    progress_header = tk.Label(
        progress_frame,
        text="📊 Analysis Progress",
        font=('Segoe UI', 11, 'bold'),
        fg=self.colors['text_primary'],
        bg=self.colors['bg_secondary']
    )
    progress_header.pack(anchor='w', padx=20, pady=(15, 10))
    
    # Steps container with scroll
    steps_canvas = tk.Canvas(progress_frame, bg=self.colors['bg_tertiary'], height=300, highlightthickness=0)
    steps_scroll = tk.Scrollbar(progress_frame, orient="vertical", command=steps_canvas.yview)
    self.ai_steps_frame = tk.Frame(steps_canvas, bg=self.colors['bg_tertiary'])
    
    self.ai_steps_frame.bind(
        "<Configure>",
        lambda e: steps_canvas.configure(scrollregion=steps_canvas.bbox("all"))
    )
    
    steps_canvas.create_window((0, 0), window=self.ai_steps_frame, anchor="nw", width=600)
    steps_canvas.configure(yscrollcommand=steps_scroll.set)
    
    steps_canvas.pack(side="left", fill="both", expand=True, padx=20, pady=(0, 15))
    steps_scroll.pack(side="right", fill="y", pady=(0, 15), padx=(0, 20))
    
    # Initial placeholder
    placeholder_label = tk.Label(
        self.ai_steps_frame,
        text="No analysis started yet. Enter a URL and click 'Start AI Analysis'",
        font=('Segoe UI', 9, 'italic'),
        fg=self.colors['text_secondary'],
        bg=self.colors['bg_tertiary']
    )
    placeholder_label.pack(padx=15, pady=30)
    
    # ===== AI Reasoning Section =====
    reasoning_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_secondary'], relief='flat', bd=2)
    reasoning_frame.pack(fill='x', padx=20, pady=(0, 20))
    
    reasoning_header = tk.Label(
        reasoning_frame,
        text="💬 AI Reasoning",
        font=('Segoe UI', 11, 'bold'),
        fg=self.colors['text_primary'],
        bg=self.colors['bg_secondary']
    )
    reasoning_header.pack(anchor='w', padx=20, pady=(15, 10))
    
    self.ai_reasoning_text = tk.Text(
        reasoning_frame,
        height=5,
        font=('Segoe UI', 9),
        bg=self.colors['bg_tertiary'],
        fg=self.colors['text_secondary'],
        relief='flat',
        wrap='word',
        state='disabled'
    )
    self.ai_reasoning_text.pack(fill='x', padx=20, pady=(0, 15))
    
    # ===== Live Console =====
    console_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_secondary'], relief='flat', bd=2)
    console_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
    
    console_header = tk.Label(
        console_frame,
        text="📄 Live Console",
        font=('Segoe UI', 11, 'bold'),
        fg=self.colors['text_primary'],
        bg=self.colors['bg_secondary']
    )
    console_header.pack(anchor='w', padx=20, pady=(15, 10))
    
    self.ai_console_text = tk.Text(
        console_frame,
        height=10,
        font=('Consolas', 9),
        bg='#000000',
        fg='#00ff00',
        relief='flat',
        wrap='word',
        state='disabled'
    )
    self.ai_console_text.pack(fill='both', expand=True, padx=20, pady=(0, 15))
    
    # Initialize AI analysis state
    self.ai_analysis_running = False
    self.ai_step_widgets = []

def start_ai_analysis(self):
    """Start AI-driven security analysis"""
    target_url = self.ai_target_var.get().strip()
    
    if not target_url or target_url == 'https://example.com':
        messagebox.showwarning("Invalid URL", "Please enter a valid target URL")
        return
    
    if self.ai_analysis_running:
        messagebox.showinfo("Analysis Running", "An AI analysis is already in progress")
        return
    
    # Validate API key
    openai_key = self.api_key_openai.get()
    if not openai_key:
        messagebox.showerror("API Key Required", 
                           "Please configure your OpenAI API key in the API Keys tab first")
        return
    
    self.ai_analysis_running = True
    self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] AI Analysis initialized")
    self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] Target: {target_url}")
    
    # Run in thread
    import threading
    thread = threading.Thread(target=self.run_ai_analysis, args=(target_url, openai_key))
    thread.daemon = True
    thread.start()

def run_ai_analysis(self, target_url: str, api_key: str):
    """Execute AI analysis in background thread"""
    import asyncio
    from services.ai_planner import AIPlanner
    from services.executor import Executor
    
    try:
        # Create event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] Initializing AI Planner...")
        
        # Initialize AI Planner
        planner = AIPlanner(api_key=api_key, model="gpt-4", temperature=0.3)
        executor = Executor(verbose=False)
        
        # Step 1: Analyze Target
        self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] Analyzing target...")
        analysis = loop.run_until_complete(planner.analyze_target(target_url))
        
        self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] Target type: {analysis.target_type.value}")
        self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] Risk level: {analysis.risk_level.value}")
        self.ai_update_reasoning(f"Target identified as: {analysis.target_type.value}\nTechnologies: {', '.join(analysis.technologies)}\nRisk: {analysis.risk_level.value}\n\nStrategy: {analysis.recommended_strategy}")
        
        # Step 2: Generate Test Plan
        self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] Generating test plan...")
        plan = loop.run_until_complete(planner.generate_test_plan(analysis))
        
        self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] Plan generated: {plan.total_steps} steps")
        self.ai_display_test_plan(plan)
        
        # Step 3: Execute Plan
        for step in plan.steps:
            self.ai_update_step_status(step.step_number, 'running')
            self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] Executing: {step.name}")
            
            result = loop.run_until_complete(executor.execute_step(step, target_url))
            
            if result.success:
                self.ai_update_step_status(step.step_number, 'completed', result)
                self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ Completed: {len(result.findings)} findings")
            else:
                self.ai_update_step_status(step.step_number, 'failed', result)
                self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] ✗ Failed: {result.error}")
            
            # AI Review
            review = loop.run_until_complete(planner.review_step_results(step, result.to_dict()))
            self.ai_update_reasoning(f"Step {step.step_number} Review:\n{review.reasoning}\nNext action: {review.next_action.value}")
            
            # Check next action
            if review.next_action.value == 'stop':
                self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] AI decided to stop testing")
                break
        
        self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Analysis complete!")
        
    except Exception as e:
        self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error: {str(e)}")
        import traceback
        self.ai_log_console(traceback.format_exc())
    
    finally:
        self.ai_analysis_running = False
        loop.close()

def ai_log_console(self, message: str):
    """Log message to AI console"""
    self.ai_console_text.config(state='normal')
    self.ai_console_text.insert('end', message + '\n')
    self.ai_console_text.see('end')
    self.ai_console_text.config(state='disabled')

def ai_update_reasoning(self, reasoning: str):
    """Update AI reasoning display"""
    self.ai_reasoning_text.config(state='normal')
    self.ai_reasoning_text.delete('1.0', 'end')
    self.ai_reasoning_text.insert('1.0', reasoning)
    self.ai_reasoning_text.config(state='disabled')

def ai_display_test_plan(self, plan):
    """Display test plan as steps"""
    # Clear existing
    for widget in self.ai_steps_frame.winfo_children():
        widget.destroy()
    
    self.ai_step_widgets = []
    
    for step in plan.steps:
        step_frame = tk.Frame(self.ai_steps_frame, bg=self.colors['bg_primary'], relief='solid', bd=1)
        step_frame.pack(fill='x', padx=10, pady=5)
        
        status_icon = tk.Label(step_frame, text="[ ]", font=('Consolas', 10), 
                              fg=self.colors['text_secondary'], bg=self.colors['bg_primary'])
        status_icon.pack(side='left', padx=10, pady=10)
        
        info_frame = tk.Frame(step_frame, bg=self.colors['bg_primary'])
        info_frame.pack(side='left', fill='x', expand=True, pady=10)
        
        name_label = tk.Label(info_frame, text=f"Step {step.step_number}: {step.name}",
                             font=('Segoe UI', 10, 'bold'), fg=self.colors['text_primary'],
                             bg=self.colors['bg_primary'], anchor='w')
        name_label.pack(fill='x')
        
        obj_label = tk.Label(info_frame, text=f"Objective: {step.objective}",
                            font=('Segoe UI', 8), fg=self.colors['text_secondary'],
                            bg=self.colors['bg_primary'], anchor='w')
        obj_label.pack(fill='x')
        
        status_label = tk.Label(info_frame, text="Pending...",
                               font=('Segoe UI', 8, 'italic'), fg=self.colors['text_secondary'],
                               bg=self.colors['bg_primary'], anchor='w')
        status_label.pack(fill='x')
        
        self.ai_step_widgets.append({
            'frame': step_frame,
            'icon': status_icon,
            'status': status_label,
            'step_number': step.step_number
        })

def ai_update_step_status(self, step_number: int, status: str, result=None):
    """Update step status visualization"""
    for widget_dict in self.ai_step_widgets:
        if widget_dict['step_number'] == step_number:
            if status == 'running':
                widget_dict['icon'].config(text="[⚙]", fg=self.colors['warning'])
                widget_dict['status'].config(text="Running...", fg=self.colors['warning'])
            elif status == 'completed':
                widget_dict['icon'].config(text="[✓]", fg=self.colors['success'])
                findings_text = f"Completed: {len(result.findings)} findings" if result else "Completed"
                widget_dict['status'].config(text=findings_text, fg=self.colors['success'])
            elif status == 'failed':
                widget_dict['icon'].config(text="[✗]", fg=self.colors['danger'])
                widget_dict['status'].config(text=f"Failed: {result.error if result else 'Unknown error'}", 
                                            fg=self.colors['danger'])
            break
