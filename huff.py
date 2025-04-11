# huffman_compression_tool.py
import heapq
import tkinter as tk
from tkinter import messagebox, scrolledtext
from collections import Counter
import threading

class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

class HuffmanCoding:
    def __init__(self):
        self.codes = {}
        self.reverse_mapping = {}

    def build_frequency_dict(self, text):
        return Counter(text)

    def build_heap(self, frequency):
        heap = [Node(char, freq) for char, freq in frequency.items()]
        heapq.heapify(heap)
        return heap

    def merge_nodes(self, heap):
        while len(heap) > 1:
            node1 = heapq.heappop(heap)
            node2 = heapq.heappop(heap)
            merged = Node(None, node1.freq + node2.freq)
            merged.left = node1
            merged.right = node2
            heapq.heappush(heap, merged)
        return heap[0]

    def build_codes_helper(self, root, current_code):
        if root is None:
            return
        if root.char is not None:
            self.codes[root.char] = current_code
            self.reverse_mapping[current_code] = root.char
        self.build_codes_helper(root.left, current_code + "0")
        self.build_codes_helper(root.right, current_code + "1")

    def build_codes(self, root):
        self.build_codes_helper(root, "")

    def get_encoded_text(self, text):
        return ''.join(self.codes[char] for char in text)

    def pad_encoded_text(self, encoded_text):
        extra_padding = 8 - len(encoded_text) % 8
        padded_info = f"{extra_padding:08b}"
        padded_text = padded_info + encoded_text + '0' * extra_padding
        return padded_text

    def compress(self, text):
        frequency = self.build_frequency_dict(text)
        heap = self.build_heap(frequency)
        root = self.merge_nodes(heap)
        self.build_codes(root)

        encoded_text = self.get_encoded_text(text)
        padded_text = self.pad_encoded_text(encoded_text)

        b = bytearray()
        for i in range(0, len(padded_text), 8):
            byte = padded_text[i:i+8]
            b.append(int(byte, 2))

        return bytes(b), root

    def remove_padding(self, padded_encoded_text):
        padded_info = padded_encoded_text[:8]
        extra_padding = int(padded_info, 2)
        return padded_encoded_text[8:-extra_padding]

    def decode_text(self, encoded_text):
        current_code = ""
        decoded_text = ""
        for bit in encoded_text:
            current_code += bit
            if current_code in self.reverse_mapping:
                decoded_text += self.reverse_mapping[current_code]
                current_code = ""
        return decoded_text

    def decompress(self, compressed_data):
        bit_string = ""
        for byte in compressed_data:
            bits = bin(byte)[2:].rjust(8, '0')
            bit_string += bits
        actual_text = self.remove_padding(bit_string)
        return self.decode_text(actual_text)

class HuffmanGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🌈 Huffman Compression Tool")
        self.root.configure(bg="#e6f2ff")

        self.huffman = HuffmanCoding()
        self.tree = None
        self.compressed_data = None
        self.original_text = ""

        self.label = tk.Label(root, text="📥 Enter Text Below:", font=("Helvetica", 14, "bold"), bg="#e6f2ff", fg="#00264d")
        self.label.pack(pady=5)

        self.input_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=8, font=("Consolas", 12), bg="#ffffff", fg="#000000")
        self.input_text.pack(pady=5)

        self.compress_button = tk.Button(root, text="🔐 Compress Text", command=self.threaded_compress, bg="#66ccff", fg="black", font=("Helvetica", 12, "bold"), padx=10, pady=5)
        self.compress_button.pack(pady=5)

        self.decompress_button = tk.Button(root, text="🔓 Decompress Text", command=self.threaded_decompress, bg="#ff9999", fg="black", font=("Helvetica", 12, "bold"), padx=10, pady=5)
        self.decompress_button.pack(pady=5)

        self.output_label = tk.Label(root, text="📤 Output:", font=("Helvetica", 14, "bold"), bg="#e6f2ff", fg="#00264d")
        self.output_label.pack(pady=5)

        self.output_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=12, state='disabled', font=("Consolas", 12), bg="#f9f9f9", fg="#000000")
        self.output_text.pack(pady=5)

    def threaded_compress(self):
        threading.Thread(target=self.compress_text).start()

    def threaded_decompress(self):
        threading.Thread(target=self.decompress_text).start()

    def compress_text(self):
        text = self.input_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Input Error", "⚠️ Please enter text to compress.")
            return
        self.original_text = text
        compressed_data, self.tree = self.huffman.compress(text)
        self.compressed_data = compressed_data

        compression_ratio = len(compressed_data) / len(text.encode('utf-8')) if text else 0

        self.output_text.config(state='normal')
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, f"✅ Compressed Data Size: {len(compressed_data)} bytes\n")
        self.output_text.insert(tk.END, f"📊 Compression Ratio: {compression_ratio:.2f}\n")
        self.output_text.insert(tk.END, f"📜 Huffman Codes: {self.huffman.codes}\n")
        self.output_text.config(state='disabled')

    def decompress_text(self):
        if self.compressed_data is None or self.tree is None:
            messagebox.showwarning("Decompression Error", "⚠️ No data to decompress.")
            return

        self.huffman.build_codes(self.tree)
        decompressed = self.huffman.decompress(self.compressed_data)

        self.output_text.config(state='normal')
        self.output_text.insert(tk.END, f"\n🔁 Decompressed Text:\n{decompressed}\n")
        self.output_text.config(state='disabled')

if __name__ == '__main__':
    app = tk.Tk()
    gui = HuffmanGUI(app)
    app.mainloop()
