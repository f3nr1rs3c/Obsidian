#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Obsidian - Advanced Pentest Encoding & Decoding Framework
Modular Multi-Layer Obfuscation and Deobfuscation Engine
"""

import hashlib
import base64
import urllib.parse
import html
import binascii
import json
import string
import re
import sys
import codecs
import zlib
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

try:
    from pyfiglet import Figlet
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    print("Missing requirements. Please install them first:")
    print("pip install pyfiglet colorama")
    sys.exit(1)

# Colors
class C:
    OK = Fore.GREEN
    WARN = Fore.YELLOW
    ERR = Fore.RED
    INFO = Fore.CYAN
    MAGENTA = Fore.MAGENTA
    BOLD = Style.BRIGHT
    RST = Style.RESET_ALL

# ==========================================
# UTILITIES & CONSTANTS
# ==========================================

def to_bytes(d):
    return d.encode('utf-8') if isinstance(d, str) else d

def to_str(d):
    return d.decode('utf-8', errors='ignore') if isinstance(d, bytes) else d

def is_printable(s):
    if not s: return False
    printable = set(string.printable)
    return all(c in printable for c in s)

morse_alphabet = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 
    'J': '.---', 'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.', 
    'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--', 'Z': '--..',
    '0': '-----', '1': '.----', '2': '..---', '3': '...--', '4': '....-', '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.',
    '.': '.-.-.-', ',': '--..--', '?': '..--..', "'": '.----.', '!': '-.-.--', '/': '-..-.', '(': '-.--.', ')': '-.--.-',
    '&': '.-...', ':': '---...', ';': '-.-.-.', '=': '-...-', '+': '.-.-.', '-': '-....-', '_': '..--.-', '"': '.-..-.', '$': '...-..-',
    '@': '.--.-.', ' ': '/'
}
reverse_morse = {v: k for k, v in morse_alphabet.items()}

# --- HASHING ---
def md5_hash(text): return hashlib.md5(text.encode()).hexdigest()
def sha1_hash(text): return hashlib.sha1(text.encode()).hexdigest()
def sha256_hash(text): return hashlib.sha256(text.encode()).hexdigest()
def sha384_hash(text): return hashlib.sha384(text.encode()).hexdigest()
def sha512_hash(text): return hashlib.sha512(text.encode()).hexdigest()

# --- CIPHERS ---
def caesar_cipher(text, shift):
    result = ""
    for char in text:
        if char.isalpha():
            if char.islower(): result += chr((ord(char) - 97 + shift) % 26 + 97)
            else: result += chr((ord(char) - 65 + shift) % 26 + 65)
        else: result += char
    return result

def caesar_decipher(text, shift): return caesar_cipher(text, -shift)

# ==========================================
# ENCODER PLUGINS & ENGINE
# ==========================================

class EncoderPlugin:
    name = "Generic"
    def encode(self, data):
        """Accepts bytes or str, returns bytes or str"""
        raise NotImplementedError

class Base64EncoderPlugin(EncoderPlugin):
    name = "Base64"
    def encode(self, data): return base64.b64encode(to_bytes(data)).decode('ascii')

class Base32EncoderPlugin(EncoderPlugin):
    name = "Base32"
    def encode(self, data): return base64.b32encode(to_bytes(data)).decode('ascii')

class HexEncoderPlugin(EncoderPlugin):
    name = "Hexadecimal"
    def encode(self, data): return to_bytes(data).hex().upper()

class URLEncoderPlugin(EncoderPlugin):
    name = "URL Encode"
    def encode(self, data): return urllib.parse.quote(to_str(data))

class HTMLEncoderPlugin(EncoderPlugin):
    name = "HTML Entities"
    def encode(self, data): return html.escape(to_str(data))

class UTF16LE_EncoderPlugin(EncoderPlugin):
    name = "UTF-16LE"
    def encode(self, data): return to_str(data).encode('utf-16le')

class ZlibEncoderPlugin(EncoderPlugin):
    name = "Zlib Deflate"
    def encode(self, data): return zlib.compress(to_bytes(data))

class Rot13EncoderPlugin(EncoderPlugin):
    name = "ROT13"
    def encode(self, data): return codecs.encode(to_str(data), 'rot_13')

class BinaryEncoderPlugin(EncoderPlugin):
    name = "Binary (010101)"
    def encode(self, data): return ' '.join(format(ord(c), '08b') for c in to_str(data))

class MorseEncoderPlugin(EncoderPlugin):
    name = "Morse Code"
    def encode(self, data): return " ".join([morse_alphabet.get(c.upper(), "?") for c in to_str(data)])


class EncoderEngine:
    def __init__(self):
        self.plugins = {
            "Base64": Base64EncoderPlugin(),
            "Base32": Base32EncoderPlugin(),
            "Hex": HexEncoderPlugin(),
            "URL Encode": URLEncoderPlugin(),
            "HTML Entities": HTMLEncoderPlugin(),
            "UTF-16LE": UTF16LE_EncoderPlugin(),
            "Zlib Deflate": ZlibEncoderPlugin(),
            "ROT13": Rot13EncoderPlugin(),
            "Binary": BinaryEncoderPlugin(),
            "Morse Code": MorseEncoderPlugin()
        }
        
    def get_plugin_names(self):
        return list(self.plugins.keys())

    def process_pipeline(self, data, pipeline_names):
        history = []
        current_data = data
        for name in pipeline_names:
            if name not in self.plugins:
                continue
            plugin = self.plugins[name]
            try:
                prev_len = len(to_bytes(current_data))
                current_data = plugin.encode(current_data)
                new_len = len(to_bytes(current_data))
                
                snippet = to_str(current_data)
                snippet = snippet[:50] + "..." if len(snippet) > 50 else snippet
                
                history.append({
                    "plugin": name,
                    "prev_len": prev_len,
                    "new_len": new_len,
                    "ratio": round(new_len / max(1, prev_len), 2),
                    "snippet": snippet
                })
            except Exception as e:
                history.append({"plugin": name, "error": str(e)})
                break
        return current_data, history


# ==========================================
# DECODER PLUGINS & ENGINE
# ==========================================

class DecoderPlugin:
    name = "Generic"
    def decode(self, data: str) -> str:
        raise NotImplementedError

class Base64Plugin(DecoderPlugin):
    name = "Base64"
    def decode(self, data):
        d = data.replace('\n', '').replace('\r', '').strip()
        if not re.match(r'^[A-Za-z0-9+/]+={0,2}$', d): return None
        d += '=' * (-len(d) % 4)
        try:
            b = base64.b64decode(d)
            try:
                res = b.decode('utf-8')
                if is_printable(res): return res
            except: pass
            try:
                res = b.decode('utf-16le')
                if is_printable(res): return res
            except: pass
        except: pass
        return None

class Base32Plugin(DecoderPlugin):
    name = "Base32"
    def decode(self, data):
        d = data.replace('\n', '').replace('\r', '').replace(' ', '').upper().strip()
        if not re.match(r'^[A-Z2-7]+=*$', d): return None
        d += '=' * (-len(d) % 8)
        try:
            res = base64.b32decode(d).decode('utf-8')
            if is_printable(res): return res
        except: pass
        return None

class HexPlugin(DecoderPlugin):
    name = "Hexadecimal"
    def decode(self, data):
        d = data.replace(' ', '').replace('0x', '').replace('\\x', '').replace('\n', '').strip()
        if not re.match(r'^[0-9A-Fa-f]+$', d): return None
        try:
            res = binascii.unhexlify(d).decode('utf-8')
            if is_printable(res): return res
        except: pass
        return None

class URLPlugin(DecoderPlugin):
    name = "URL Decode"
    def decode(self, data):
        if '%' not in data: return None
        try:
            res = urllib.parse.unquote(data)
            if is_printable(res): return res
        except: pass
        return None

class HTMLPlugin(DecoderPlugin):
    name = "HTML Entities"
    def decode(self, data):
        if '&' not in data and ';' not in data: return None
        try:
            res = html.unescape(data)
            if is_printable(res): return res
        except: pass
        return None

class Cisco7Plugin(DecoderPlugin):
    name = "Cisco Type 7"
    def decode(self, hash_str):
        keys = [
            0x64, 0x73, 0x66, 0x64, 0x3b, 0x6b, 0x66, 0x6f, 0x41, 0x2c, 0x2e, 0x69, 0x79, 0x65, 0x77, 0x72,
            0x6b, 0x6c, 0x64, 0x4a, 0x4b, 0x44, 0x48, 0x53, 0x55, 0x42, 0x73, 0x67, 0x76, 0x63, 0x61, 0x36,
            0x39, 0x38, 0x33, 0x34, 0x6e, 0x63, 0x64, 0x35, 0x36, 0x39, 0x38, 0x33, 0x34, 0x33, 0x34, 0x6e,
            0x63, 0x64, 0x35
        ]
        hash_str = hash_str.strip()
        if len(hash_str) < 4 or not re.match(r'^[0-9A-Fa-f]+$', hash_str): return None
        try:
            index = int(hash_str[:2])
            if index > 15: return None
            dec = ""
            for i in range(2, len(hash_str), 2):
                dec += chr(int(hash_str[i:i+2], 16) ^ keys[index % len(keys)])
                index += 1
            if is_printable(dec): return dec
        except: pass
        return None

class Rot13Plugin(DecoderPlugin):
    name = "ROT13"
    def decode(self, data):
        if not any(c.isalpha() for c in data): return None
        try:
            res = codecs.encode(data, 'rot_13')
            if is_printable(res): return res
        except: pass
        return None

class JWTPlugin(DecoderPlugin):
    name = "JWT (JSON Web Token)"
    def decode(self, data):
        parts = data.strip().split('.')
        if len(parts) in [2, 3]:
            out = []
            for p in parts[:2]:
                p += '=' * (-len(p) % 4)
                try:
                    dec = base64.urlsafe_b64decode(p).decode('utf-8')
                    parsed = json.loads(dec)
                    out.append(json.dumps(parsed, indent=2))
                except: return None
            return "\n".join(out)
        return None

class BinaryPlugin(DecoderPlugin):
    name = "Binary (010101)"
    def decode(self, data):
        d = data.replace(' ', '').replace('\n', '').strip()
        if len(d) % 8 != 0 or not all(c in '01' for c in d) or len(d) == 0: return None
        try:
            res = ''.join(chr(int(d[i:i+8], 2)) for i in range(0, len(d), 8))
            if is_printable(res): return res
        except: pass
        return None

class MorsePlugin(DecoderPlugin):
    name = "Morse Code"
    def decode(self, data):
        d = data.strip()
        if not d or not all(c in '.-/ \n\r' for c in d): return None
        words = d.split(' ')
        dec = ''
        for w in words:
            if not w: continue
            if w in reverse_morse: dec += reverse_morse[w]
            else: return None
        if is_printable(dec): return dec
        return None

class UnicodePlugin(DecoderPlugin):
    name = "Unicode/Hex Escapes"
    def decode(self, data):
        if '\\' not in data: return None
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                res = codecs.decode(data, 'unicode_escape')
            if is_printable(res): return res
        except: pass
        return None

class ZlibPlugin(DecoderPlugin):
    name = "Zlib Deflate (Gzip/Hex/B64)"
    def decode(self, data):
        try:
            b = binascii.unhexlify(data.replace(' ', '').replace('0x', '').replace('\\x', ''))
            res = zlib.decompress(b).decode('utf-8')
            if is_printable(res): return res
        except: pass
        
        try:
            d = data.replace('\n', '').replace('\r', '').strip()
            d += '=' * (-len(d) % 4)
            b = base64.b64decode(d)
            res = zlib.decompress(b).decode('utf-8')
            if is_printable(res): return res
        except: pass
        return None

class DecoderEngine:
    def __init__(self):
        self.plugins = [
            Base64Plugin(), Base32Plugin(), HexPlugin(), URLPlugin(),
            HTMLPlugin(), ZlibPlugin(), MorsePlugin(), BinaryPlugin(),
            JWTPlugin(), Rot13Plugin(), Cisco7Plugin(), UnicodePlugin()
        ]
        
    def analyze(self, data: str, depth=0, max_depth=5, current_path=None):
        if current_path is None:
            current_path = []
            
        if depth >= max_depth:
            return []
            
        leaf_results = []
        has_child = False
        
        for plugin in self.plugins:
            res = plugin.decode(data)
            
            if res and res != data and str(res).strip():
                if any(res == step_res for _, step_res in current_path):
                    continue
                
                has_child = True
                new_path = current_path + [(plugin.name, res)]
                sub_results = self.analyze(res, depth + 1, max_depth, new_path)
                
                if sub_results: leaf_results.extend(sub_results)
                else: leaf_results.append(new_path)
                    
        return leaf_results


def print_decode_tree(paths):
    if not paths:
        print(f"{C.ERR}[-] Could not find any meaningful decode format.{C.RST}\n")
        return

    print(f"{C.OK}[+] Analysis Complete. Discovered {len(paths)} potential paths:{C.RST}\n")
    for i, path in enumerate(paths, 1):
        print(f"{C.INFO}--- Path #{i} ({len(path)} layers) ---{C.RST}")
        for j, (plugin_name, result) in enumerate(path):
            prefix = "  " * j + "└─ " if j > 0 else "└─ "
            print(f"{C.WARN}{prefix}[{plugin_name}]{C.RST}")
        
        final_result = path[-1][1]
        print(f"\n{C.OK}Final Result:{C.RST}\n{final_result}\n")
        print("-" * 40)


# ==========================================
# MENUS
# ==========================================
def print_banner():
    f = Figlet(font='slant', width=100)
    print(C.ERR + f.renderText('Obsidian') + C.RST)
    print(C.MAGENTA + "          | - |  By : Red Team Operations Script | - |         " + C.RST)
    print()

def main_menu():
    engine = DecoderEngine()
    
    while True:
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print_banner()
        print(f"{C.WARN}--- MAIN MENU ---{C.RST}")
        print(f"{C.INFO}1.{C.RST} Obfuscation Pipeline Builder (Multi-Layer Encode)")
        print(f"{C.INFO}2.{C.RST} Deep Analysis (Multi-Layer Decode)")
        print(f"{C.INFO}3.{C.RST} Hashing (MD5, SHA1, SHA256...)")
        print(f"{C.INFO}4.{C.RST} Manual Encoders / Decoders / Ciphers")
        print(f"{C.INFO}0.{C.RST} Exit\n")
        
        choice = input(f"{C.BOLD}Select an option: {C.RST}")
        
        if choice == '1':
            pipeline_builder_menu()
        elif choice == '2':
            print()
            text = input(f"{C.WARN}Enter obfuscated/encoded text: {C.RST}")
            if text:
                print(f"\n{C.INFO}[*] Deep Analyzing (Max Depth: 5): {C.RST}{text[:60]}...")
                paths = engine.analyze(text, max_depth=5)
                print_decode_tree(paths)
            input("Press Enter to continue...")
        elif choice == '3':
            hashing_menu()
        elif choice == '4':
            manual_menu()
        elif choice == '0':
            print("Exiting Obsidian. Goodbye!")
            break
        else:
            print("Invalid option!")

def pipeline_builder_menu():
    engine = EncoderEngine()
    plugins = engine.get_plugin_names()
    
    while True:
        print(f"\n{C.WARN}--- OBFUSCATION PIPELINE BUILDER ---{C.RST}")
        print("1. Build Manual Chain")
        print("2. Use Preset Profiles")
        print("0. Back")
        
        choice = input("Select: ")
        
        if choice == '1':
            print(f"\n{C.INFO}Available Encoders:{C.RST}")
            for i, p in enumerate(plugins, 1):
                print(f"{i}. {p}")
            print(f"\nExample input: 6,1,4 (UTF-16LE -> Base64 -> URL Encode)")
            chain_input = input("Enter chain order (comma separated): ")
            try:
                indexes = [int(x.strip()) - 1 for x in chain_input.split(',')]
                pipeline = [plugins[i] for i in indexes if 0 <= i < len(plugins)]
                text = input(f"{C.WARN}Enter text to obfuscate: {C.RST}")
                run_pipeline(engine, text, pipeline)
            except:
                print(f"{C.ERR}Invalid input.{C.RST}")
        elif choice == '2':
            print(f"\n{C.INFO}Presets:{C.RST}")
            print("1. PowerShell Base64 Obfuscation (UTF-16LE -> Base64)")
            print("2. Web WAF Evasion (Base64 -> URL Encode -> HTML Entities)")
            print("3. Deep Obfuscation (Zlib -> Base64 -> Hex -> ROT13)")
            p_choice = input("Select Preset: ")
            
            pipeline = []
            if p_choice == '1': pipeline = ["UTF-16LE", "Base64"]
            elif p_choice == '2': pipeline = ["Base64", "URL Encode", "HTML Entities"]
            elif p_choice == '3': pipeline = ["Zlib Deflate", "Base64", "Hex", "ROT13"]
            else: continue
            
            text = input(f"{C.WARN}Enter text to obfuscate: {C.RST}")
            run_pipeline(engine, text, pipeline)
        elif choice == '0':
            break

def run_pipeline(engine, text, pipeline):
    print(f"\n{C.INFO}[*] Running Pipeline: {' -> '.join(pipeline)}{C.RST}")
    result, history = engine.process_pipeline(text, pipeline)
    
    print(f"\n{C.OK}[+] Pipeline Execution Complete!{C.RST}")
    for i, step in enumerate(history, 1):
        if "error" in step:
            print(f"  {C.ERR}Step {i}: [{step['plugin']}] - FAILED: {step['error']}{C.RST}")
            break
        print(f"  {C.INFO}Step {i}: [{step['plugin']}]{C.RST} - Size: {step['prev_len']}B -> {step['new_len']}B (Ratio: {step['ratio']}x)")
        print(f"    Preview: {step['snippet']}")
    
    final_text = to_str(result)
    print(f"\n{C.OK}Final Payload:{C.RST}\n{final_text}\n")
    
    save = input("Save report to markdown? (y/n): ")
    if save.lower() == 'y':
        filename = f"obfuscation_report.md"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# Obsidian Obfuscation Report\n\n")
            f.write(f"**Original Text:** {text}\n\n")
            f.write(f"**Pipeline:** {' -> '.join(pipeline)}\n\n")
            f.write("## Execution Steps\n")
            for i, step in enumerate(history, 1):
                if "error" in step:
                    f.write(f"{i}. **{step['plugin']}**: FAILED - {step['error']}\n")
                else:
                    f.write(f"{i}. **{step['plugin']}**: {step['prev_len']}B -> {step['new_len']}B (Ratio: {step['ratio']}x)\n")
            f.write(f"\n## Final Payload\n```\n{final_text}\n```\n")
        print(f"{C.OK}[+] Report saved to {filename}{C.RST}")

def hashing_menu():
    print(f"\n{C.WARN}--- HASHING ---{C.RST}")
    print("1. MD5\n2. SHA1\n3. SHA256\n4. SHA384\n5. SHA512\n0. Back")
    choice = input("Select: ")
    if choice in ['1','2','3','4','5']:
        text = input("Enter Text: ")
        if choice == '1': print(f"{C.OK}MD5: {C.RST}{md5_hash(text)}")
        elif choice == '2': print(f"{C.OK}SHA1: {C.RST}{sha1_hash(text)}")
        elif choice == '3': print(f"{C.OK}SHA256: {C.RST}{sha256_hash(text)}")
        elif choice == '4': print(f"{C.OK}SHA384: {C.RST}{sha384_hash(text)}")
        elif choice == '5': print(f"{C.OK}SHA512: {C.RST}{sha512_hash(text)}")
        input("Press Enter to continue...")

def manual_menu():
    print(f"\n{C.WARN}--- MANUAL ENCODE/DECODE ---{C.RST}")
    print("1. Encode (Base64, Hex, URL, HTML...)")
    print("2. Decode (Base64, Hex, URL, HTML...)")
    print("3. Ciphers (Caesar, ROT13, Cisco7)")
    print("0. Back")
    choice = input("Select: ")
    if choice == '1':
        print("\n1. Base64\n2. Hex\n3. URL\n4. HTML\n5. Binary\n6. Morse")
        c = input("Select: ")
        text = input("Text: ")
        engine = EncoderEngine()
        try:
            if c == '1': print(to_str(engine.plugins["Base64"].encode(text)))
            elif c == '2': print(to_str(engine.plugins["Hex"].encode(text)))
            elif c == '3': print(to_str(engine.plugins["URL Encode"].encode(text)))
            elif c == '4': print(to_str(engine.plugins["HTML Entities"].encode(text)))
            elif c == '5': print(to_str(engine.plugins["Binary"].encode(text)))
            elif c == '6': print(to_str(engine.plugins["Morse Code"].encode(text)))
        except Exception as e: print(f"{C.ERR}Error: {e}{C.RST}")
        input("Press Enter to continue...")
    elif choice == '2':
        print("\n1. Base64\n2. Hex\n3. URL\n4. HTML\n5. Binary\n6. Morse")
        c = input("Select: ")
        text = input("Text: ")
        try:
            if c == '1': print(base64.b64decode(text).decode('utf-8'))
            elif c == '2': print(binascii.unhexlify(text).decode('utf-8'))
            elif c == '3': print(urllib.parse.unquote(text))
            elif c == '4': print(html.unescape(text))
            elif c == '5': print(''.join(chr(int(text[i:i+8], 2)) for i in range(0, len(text), 8)))
            elif c == '6': print(''.join(reverse_morse[w] for w in text.split(' ') if w in reverse_morse))
        except Exception as e: print(f"{C.ERR}Error: {e}{C.RST}")
        input("Press Enter to continue...")
    elif choice == '3':
        print("\n1. Caesar Enc\n2. Caesar Dec\n3. ROT13\n4. Cisco Type 7 Dec")
        c = input("Select: ")
        text = input("Text: ")
        if c == '1': print(caesar_cipher(text, int(input("Shift: "))))
        elif c == '2': print(caesar_decipher(text, int(input("Shift: "))))
        elif c == '3': print(codecs.encode(text, 'rot_13'))
        elif c == '4':
            engine = DecoderEngine()
            for p in engine.plugins:
                if p.name == "Cisco Type 7":
                    res = p.decode(text)
                    print(res if res else 'Invalid')
        input("Press Enter to continue...")


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\nExiting Obsidian. Goodbye!")
        sys.exit(0)
