import React, { useState, useEffect } from 'react';
import {
  Utensils, ShieldCheck, HeartHandshake, Search, Bike, Truck, PackageCheck,
  Building2, Users, Layers, Database, Languages, ArrowRight, CheckCircle,
  PlusCircle, Calendar, CalendarCheck, Clock, MapPin, ChefHat, HandHeart,
  Boxes, CalendarClock, MessageSquareText, Bot, X, Send, LogOut, CheckCheck,
  AlertCircle, AlertTriangle, Info, RefreshCw
} from 'lucide-react';

const API_BASE = '/api/v1';

export default function App() {
  const [currentView, setCurrentView] = useState('landing');
  const [currentUser, setCurrentUser] = useState(() => {
    const saved = localStorage.getItem('foodshare_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [currentLang, setCurrentLang] = useState(() => localStorage.getItem('foodshare_lang') || 'en');
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chatMessages, setChatMessages] = useState([
    { sender: 'ai', text: 'Hello! 👋 How can I help you today?' }
  ]);
  const [chatInput, setChatInput] = useState('');
  const [activeLogisticsTab, setActiveLogisticsTab] = useState('donor');
  const [authModal, setAuthModal] = useState({ open: false, tab: 'login' });
  const [loginForm, setLoginForm] = useState({ email: '', password: '' });
  const [toast, setToast] = useState(null);

  // Live Stats State
  const [stats, setStats] = useState({
    activeDonations: 4,
    verifiedNgos: 2,
    volunteers: 2,
    deliveries: 1
  });

  const showToast = (title, message, type = 'success') => {
    setToast({ title, message, type });
    setTimeout(() => setToast(null), 4000);
  };

  const handleLanguageChange = (lang) => {
    setCurrentLang(lang);
    localStorage.setItem('foodshare_lang', lang);
    document.documentElement.setAttribute('dir', lang === 'ar' ? 'rtl' : 'ltr');
  };

  const handleLogin = (e) => {
    e.preventDefault();
    // Simulate login API call or connect to FastAPI /api/v1/auth/login
    const mockUsers = {
      'donor@greenbites.com': { id: 2, name: 'Chef Rajesh Verma', role: 'donor', org: 'Green Bites Banquet' },
      'ngo@annaseva.org': { id: 4, name: 'Aarti Deshmukh', role: 'ngo', org: 'Anna Seva Foundation', reg: 'NGO-MH-2023-8891' },
      'volunteer@foodshare.org': { id: 6, name: 'Karan Patil', role: 'volunteer' },
      'admin@foodshare.org': { id: 1, name: 'System Administrator', role: 'admin' }
    };
    const user = mockUsers[loginForm.email.toLowerCase()];
    if (user && loginForm.password) {
      setCurrentUser(user);
      localStorage.setItem('foodshare_user', JSON.stringify(user));
      setAuthModal({ open: false, tab: 'login' });
      showToast('Welcome!', `Logged in as ${user.name}`);
      setCurrentView(user.role);
    } else {
      showToast('Login Failed', 'Invalid credentials. Try demo logins.', 'error');
    }
  };

  const handleLogout = () => {
    setCurrentUser(null);
    localStorage.removeItem('foodshare_user');
    setCurrentView('landing');
    showToast('Signed Out', 'You have been logged out.');
  };

  const handleChatSubmit = (e) => {
    e.preventDefault();
    if (!chatInput.trim()) return;
    const userMsg = chatInput.trim();
    setChatMessages((prev) => [...prev, { sender: 'user', text: userMsg }]);
    setChatInput('');

    setTimeout(() => {
      let reply = "I'm sorry, I couldn't resolve that. Please try another question or contact the administrator.";
      const lower = userMsg.toLowerCase();
      if (lower.includes('donate')) {
        reply = "To donate food: 1. Sign in as Donor. 2. Open Donor Dashboard. 3. Enter food specifications, quantity, safe expiry deadline, and pickup location. 4. Click 'Publish Donation to Pool'.";
      } else if (lower.includes('schedule') || lower.includes('pickup')) {
        reply = "To schedule a pickup: Open Logistics -> Donor Logistics. Select your donation, set pickup date/time and window (e.g. Evening 18:30–20:30), choose thermal packaging, and confirm.";
      } else if (lower.includes('ngo') || lower.includes('claim')) {
        reply = "For NGOs: Sign in with a verified account, browse available food under 'Find Food', choose required quantity, state intended purpose, and claim food to queue delivery.";
      } else if (lower.includes('volunteer')) {
        reply = "For Volunteers: Log in, visit Volunteer Dashboard, select an available task from the FIFO queue, click 'Accept Task', and advance progress to Picked Up -> In Transit -> Delivered.";
      } else if (lower.includes('track')) {
        reply = "Track deliveries under Logistics -> NGO Logistics. Follow the 5-step pipeline: Accepted -> Scheduled -> Picked Up -> In Transit -> Delivered.";
      } else if (lower.includes('language')) {
        reply = "Change language via the selector dropdown in the top header. FoodShare supports 9 languages including Arabic (RTL).";
      }
      setChatMessages((prev) => [...prev, { sender: 'ai', text: reply }]);
    }, 300);
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#FFFCF5] text-[#183629]">
      {/* Toast Notification */}
      {toast && (
        <div className="fixed top-20 right-5 z-50 max-w-sm w-full bg-[#183629] text-[#FFFCF5] p-4 rounded-xl shadow-2xl border border-[#DCE8D8]/30 flex items-start space-x-3">
          <div className="text-emerald-400 mt-0.5"><CheckCircle className="w-5 h-5" /></div>
          <div className="flex-1">
            <h4 className="text-sm font-bold">{toast.title}</h4>
            <p className="text-xs text-[#DCE8D8] mt-0.5">{toast.message}</p>
          </div>
        </div>
      )}

      {/* Header */}
      <header className="sticky top-0 z-40 bg-[#234B36] text-[#FFFCF5] shadow-md border-b border-[#183629]/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setCurrentView('landing')}>
            <div className="w-10 h-10 rounded-xl bg-[#F5EBD7] text-[#234B36] flex items-center justify-center font-bold text-xl shadow">
              <Utensils className="w-5 h-5 text-[#234B36]" />
            </div>
            <div>
              <span className="font-extrabold text-xl tracking-tight">FoodShare</span>
              <span className="hidden sm:inline-block text-xs text-[#DCE8D8] ml-2 px-2 py-0.5 rounded-full bg-[#183629]">
                Capstone Project
              </span>
            </div>
          </div>

          <nav className="hidden md:flex items-center space-x-2 text-sm font-medium">
            <button onClick={() => setCurrentView('landing')} className="px-3 py-1.5 rounded-lg hover:bg-[#183629]">Home</button>
            <button onClick={() => setCurrentView('donor')} className="px-3 py-1.5 rounded-lg hover:bg-[#183629]">Donate Food</button>
            <button onClick={() => setCurrentView('ngo')} className="px-3 py-1.5 rounded-lg hover:bg-[#183629]">Find Food</button>
            <button onClick={() => setCurrentView('volunteer')} className="px-3 py-1.5 rounded-lg hover:bg-[#183629]">Volunteer</button>
            <button onClick={() => setCurrentView('logistics')} className="px-3 py-1.5 rounded-lg bg-[#183629]/60 hover:bg-[#183629] text-[#F5EBD7] flex items-center space-x-1 border border-[#DCE8D8]/20">
              <Truck className="w-4 h-4" />
              <span>Logistics</span>
            </button>
            <button onClick={() => setCurrentView('ds')} className="px-3 py-1.5 rounded-lg hover:bg-[#183629]">Data Structures</button>
          </nav>

          <div className="flex items-center space-x-3">
            <select
              value={currentLang}
              onChange={(e) => handleLanguageChange(e.target.value)}
              className="bg-[#183629] text-[#FFFCF5] border border-[#DCE8D8]/30 text-xs rounded-lg px-2.5 py-1.5"
            >
              <option value="en">English (EN)</option>
              <option value="mr">मराठी (MR)</option>
              <option value="hi">हिन्दी (HI)</option>
              <option value="es">Español (ES)</option>
              <option value="ar">العربية (AR)</option>
            </select>

            {currentUser ? (
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setCurrentView(currentUser.role)}
                  className="px-3 py-1 rounded-xl bg-[#183629] text-xs font-bold text-[#FFFCF5] border border-[#DCE8D8]/30"
                >
                  {currentUser.name.split(' ')[0]} ({currentUser.role.toUpperCase()})
                </button>
                <button onClick={handleLogout} className="p-1.5 rounded-xl hover:bg-[#183629] text-[#DCE8D8]">
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <button
                onClick={() => setAuthModal({ open: true, tab: 'login' })}
                className="px-4 py-1.5 rounded-xl bg-[#F5EBD7] text-[#234B36] font-bold text-xs shadow hover:bg-white"
              >
                Sign In
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
        {currentView === 'landing' && (
          <div className="space-y-16">
            {/* Hero */}
            <div className="text-center py-16 bg-gradient-to-b from-[#234B36] to-[#183629] text-[#FFFCF5] rounded-3xl p-8 shadow-xl">
              <span className="inline-flex items-center space-x-2 bg-[#DCE8D8]/15 px-4 py-1 rounded-full text-xs text-[#F5EBD7] mb-4">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <span>Engineered with Python, Data Structures & Relational DBMS</span>
              </span>
              <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight">Share Food, Spread Hope</h1>
              <p className="max-w-2xl mx-auto text-base sm:text-lg text-[#DCE8D8] mt-4">
                FoodShare bridges surplus food from banquets, caterers, and bakeries directly to verified charities and hunger shelters in real time.
              </p>
              <div className="flex flex-wrap justify-center gap-4 mt-8">
                <button onClick={() => setCurrentView('donor')} className="px-6 py-3 rounded-xl bg-[#F5EBD7] text-[#234B36] font-bold text-sm shadow hover:bg-white flex items-center space-x-2">
                  <HeartHandshake className="w-4 h-4" />
                  <span>Donate Surplus Food</span>
                </button>
                <button onClick={() => setCurrentView('ngo')} className="px-6 py-3 rounded-xl bg-[#183629] text-[#FFFCF5] border border-[#DCE8D8]/30 font-semibold text-sm hover:bg-[#234B36] flex items-center space-x-2">
                  <Search className="w-4 h-4 text-[#DCE8D8]" />
                  <span>Discover Food for NGOs</span>
                </button>
                <button onClick={() => setCurrentView('volunteer')} className="px-6 py-3 rounded-xl bg-[#DCE8D8]/20 text-[#FFFCF5] border border-[#DCE8D8]/20 text-sm hover:bg-[#DCE8D8]/30 flex items-center space-x-2">
                  <Bike className="w-4 h-4 text-emerald-400" />
                  <span>Deliver as Volunteer</span>
                </button>
              </div>
            </div>

            {/* About Us Section */}
            <section id="about" className="py-12 px-6 rounded-3xl bg-[#F5EBD7]/50 border border-[#234B36]/10">
              <div className="text-center max-w-3xl mx-auto mb-10">
                <span className="inline-flex items-center space-x-1.5 px-3.5 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-[#234B36]/10 text-[#234B36]">
                  <HeartHandshake className="w-3.5 h-3.5" />
                  <span>About Us — Who We Are</span>
                </span>
                <h2 className="text-3xl font-extrabold text-[#183629] mt-3">Transforming Surplus Food into Sustenance & Hope</h2>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-[#FFFCF5] p-6 rounded-2xl border border-[#234B36]/15 shadow-sm space-y-2">
                  <div className="w-10 h-10 rounded-xl bg-[#234B36] text-[#FFFCF5] flex items-center justify-center font-bold mb-3">
                    <ShieldCheck className="w-5 h-5" />
                  </div>
                  <h3 className="font-extrabold text-base text-[#183629]">Our Identity</h3>
                  <p className="text-xs text-[#234B36] leading-relaxed">
                    FoodShare is a technology-driven food donation and distribution platform that connects food donors, NGOs, volunteers, and recipients.
                  </p>
                </div>

                <div className="bg-[#FFFCF5] p-6 rounded-2xl border border-[#234B36]/15 shadow-sm space-y-2">
                  <div className="w-10 h-10 rounded-xl bg-[#234B36] text-[#FFFCF5] flex items-center justify-center font-bold mb-3">
                    <PlusCircle className="w-5 h-5" />
                  </div>
                  <h3 className="font-extrabold text-base text-[#183629]">Our Mission</h3>
                  <p className="text-xs text-[#234B36] leading-relaxed">
                    To reduce food waste and ensure surplus food reaches people who need it through an organized, transparent, and efficient distribution system.
                  </p>
                </div>

                <div className="bg-[#FFFCF5] p-6 rounded-2xl border border-[#234B36]/15 shadow-sm space-y-2">
                  <div className="w-10 h-10 rounded-xl bg-[#234B36] text-[#FFFCF5] flex items-center justify-center font-bold mb-3">
                    <Building2 className="w-5 h-5" />
                  </div>
                  <h3 className="font-extrabold text-base text-[#183629]">Our Vision</h3>
                  <p className="text-xs text-[#234B36] leading-relaxed">
                    A future where edible surplus food is not wasted while people in our communities face hunger.
                  </p>
                </div>
              </div>
            </section>
          </div>
        )}

        {/* Dashboard Views */}
        {currentView === 'donor' && (
          <div className="space-y-6">
            <div className="bg-[#234B36] text-[#FFFCF5] p-6 rounded-3xl shadow flex justify-between items-center">
              <div>
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-[#183629] text-[#DCE8D8]">Donor Portal</span>
                <h1 className="text-2xl font-black mt-1">Welcome, {currentUser ? currentUser.name : 'Rahul Sharma'}!</h1>
                <p className="text-xs text-[#DCE8D8] mt-0.5">Green Bites Banquet • Active Food Donor</p>
              </div>
              <button onClick={() => setCurrentView('logistics')} className="px-4 py-2 rounded-xl bg-[#F5EBD7] text-[#234B36] font-bold text-xs">
                Schedule Pickup in Logistics
              </button>
            </div>
            <p className="text-xs text-[#234B36]">Listing active donations and tracking distribution receipts.</p>
          </div>
        )}

        {/* Logistics View */}
        {currentView === 'logistics' && (
          <div className="space-y-6">
            <div className="bg-[#234B36] text-[#FFFCF5] p-6 rounded-3xl shadow">
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-[#183629] text-[#DCE8D8]">Operations & Logistics</span>
              <h1 className="text-2xl font-black mt-1">FoodShare Logistics Management</h1>
              <div className="flex gap-2 mt-4">
                <button onClick={() => setActiveLogisticsTab('donor')} className={`px-4 py-1.5 rounded-xl text-xs font-bold ${activeLogisticsTab === 'donor' ? 'bg-[#F5EBD7] text-[#234B36]' : 'bg-[#183629] text-[#FFFCF5]'}`}>Donor Scheduling</button>
                <button onClick={() => setActiveLogisticsTab('ngo')} className={`px-4 py-1.5 rounded-xl text-xs font-bold ${activeLogisticsTab === 'ngo' ? 'bg-[#F5EBD7] text-[#234B36]' : 'bg-[#183629] text-[#FFFCF5]'}`}>NGO Tracking</button>
                <button onClick={() => setActiveLogisticsTab('admin')} className={`px-4 py-1.5 rounded-xl text-xs font-bold ${activeLogisticsTab === 'admin' ? 'bg-[#F5EBD7] text-[#234B36]' : 'bg-[#183629] text-[#FFFCF5]'}`}>Admin Inventory</button>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Floating AI Chatbot Button & Drawer Window */}
      <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end">
        {isChatOpen && (
          <div className="mb-3 w-[calc(100vw-2.5rem)] sm:w-96 max-w-[390px] bg-[#FFFCF5] rounded-3xl shadow-2xl border border-[#234B36]/20 overflow-hidden flex flex-col h-[520px] max-h-[82vh]">
            <div className="bg-[#234B36] text-[#FFFCF5] px-4 py-3.5 flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 rounded-full bg-[#F5EBD7] text-[#234B36] flex items-center justify-center font-bold">
                  <Bot className="w-5 h-5 text-[#234B36]" />
                </div>
                <div>
                  <h4 className="font-bold text-sm">FoodShare AI Assistant</h4>
                  <div className="flex items-center space-x-1 text-[11px] text-emerald-300">
                    <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                    <span>FAQ Inverted Index Online</span>
                  </div>
                </div>
              </div>
              <button onClick={() => setIsChatOpen(false)} className="p-1 rounded-lg text-[#DCE8D8] hover:text-[#FFFCF5]">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="flex-1 p-4 overflow-y-auto space-y-3 text-xs custom-scrollbar">
              {chatMessages.map((msg, i) => (
                <div key={i} className={`flex items-start ${msg.sender === 'user' ? 'justify-end' : 'space-x-2'}`}>
                  {msg.sender === 'ai' && (
                    <div className="w-7 h-7 rounded-full bg-[#234B36] text-[#FFFCF5] flex items-center justify-center font-bold text-xs shrink-0">
                      AI
                    </div>
                  )}
                  <div className={`p-3 rounded-2xl max-w-[85%] leading-relaxed ${msg.sender === 'user' ? 'bg-[#234B36] text-[#FFFCF5]' : 'bg-[#F5EBD7] text-[#183629]'}`}>
                    {msg.text}
                  </div>
                </div>
              ))}
            </div>

            <form onSubmit={handleChatSubmit} className="p-3 border-t border-[#234B36]/15 bg-white flex items-center space-x-2">
              <input
                type="text"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                placeholder="Ask FoodShare AI a question..."
                className="flex-1 px-3 py-2 text-xs rounded-xl border border-[#234B36]/20 focus:outline-none focus:ring-1 focus:ring-[#234B36]"
              />
              <button type="submit" className="p-2 rounded-xl bg-[#234B36] text-[#FFFCF5]">
                <Send className="w-4 h-4" />
              </button>
            </form>
          </div>
        )}

        <div className="relative group">
          <div className="absolute right-full mr-3 top-1/2 -translate-y-1/2 pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity bg-[#183629] text-[#FFFCF5] text-xs font-semibold px-3 py-1.5 rounded-xl shadow whitespace-nowrap hidden sm:block">
            Chat with FoodShare AI
          </div>
          <button
            onClick={() => setIsChatOpen(!isChatOpen)}
            className="w-14 h-14 rounded-full bg-[#234B36] hover:bg-[#183629] text-[#FFFCF5] shadow-2xl flex items-center justify-center border-2 border-[#F5EBD7] hover:scale-105 active:scale-95 transition"
          >
            {isChatOpen ? <X className="w-6 h-6" /> : <MessageSquareText className="w-6 h-6" />}
          </button>
        </div>
      </div>
    </div>
  );
}
