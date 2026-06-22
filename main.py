"""
My-Simubursa — Simulasi Matching Engine Bursa
Struktur Data: AVL Tree (hierarki harga) + Doubly Linked List Queue (antrian FIFO per harga).
"""

import time
import os

# DOUBLY LINKED LIST — Antrian FIFO per level harga
class DLLNode:
    """Node untuk Doubly Linked List (satu order)"""
    def __init__(self, order_id, trader, qty):
        self.order_id = order_id
        self.trader   = trader
        self.qty      = qty
        self.prev     = None
        self.next     = None


class DLLQueue:
    """
    Doubly Linked List sebagai antrian FIFO.
    Enqueue di tail (belakang), Dequeue dari head (depan).
    """
    def __init__(self):
        self.head  = None
        self.tail  = None
        self.size  = 0

    def enqueue(self, order_id, trader, qty):
        """Tambahkan order ke belakang antrian — O(1)"""
        node = DLLNode(order_id, trader, qty)
        if self.tail is None:
            self.head = self.tail = node
        else:
            node.prev    = self.tail
            self.tail.next = node
            self.tail    = node
        self.size += 1

    def dequeue(self):
        """Ambil dan hapus order dari depan antrian — O(1)"""
        if self.head is None:
            return None
        node       = self.head
        self.head  = self.head.next
        if self.head:
            self.head.prev = None
        else:
            self.tail = None
        self.size -= 1
        return node

    def peek(self):
        """Lihat order terdepan tanpa menghapus — O(1)"""
        return self.head

    def remove_by_id(self, order_id):
        """Hapus order tertentu dari antrian — O(n)"""
        cur = self.head
        while cur:
            if cur.order_id == order_id:
                if cur.prev:
                    cur.prev.next = cur.next
                else:
                    self.head = cur.next
                if cur.next:
                    cur.next.prev = cur.prev
                else:
                    self.tail = cur.prev
                self.size -= 1
                return True
            cur = cur.next
        return False

    def is_empty(self):
        return self.size == 0

    def to_list(self):
        """Kembalikan semua order sebagai list — untuk tampilan"""
        result, cur = [], self.head
        while cur:
            result.append((cur.order_id, cur.trader, cur.qty))
            cur = cur.next
        return result

# AVL TREE — Hierarki level harga
class AVLNode:
    """
    Node AVL Tree.
    Setiap node = satu level harga.
    queue = DLLQueue berisi order pada harga ini.
    """
    def __init__(self, price):
        self.price  = price
        self.queue  = DLLQueue()   # Antrian FIFO order di harga ini
        self.left   = None
        self.right  = None
        self.height = 1

class AVLTree:
    """
    AVL Tree self-balancing untuk manajemen level harga.
    Insert/Delete/Search: O(log n)
    """
    def _h(self, node):
        return node.height if node else 0

    def _bf(self, node):
        return self._h(node.left) - self._h(node.right)

    def _update_height(self, node):
        node.height = 1 + max(self._h(node.left), self._h(node.right))

    def _rotate_right(self, z):
        """Rotasi kanan (LL case)"""
        y      = z.left
        T3     = y.right
        y.right = z
        z.left  = T3
        self._update_height(z)
        self._update_height(y)
        return y

    def _rotate_left(self, z):
        """Rotasi kiri (RR case)"""
        y      = z.right
        T2     = y.left
        y.left  = z
        z.right = T2
        self._update_height(z)
        self._update_height(y)
        return y

    def _balance(self, node):
        """Lakukan rotasi bila perlu setelah insert/delete"""
        self._update_height(node)
        bf = self._bf(node)

        if bf > 1:   # Left heavy
            if self._bf(node.left) < 0:          # LR case
                node.left = self._rotate_left(node.left)
            return self._rotate_right(node)

        if bf < -1:  # Right heavy
            if self._bf(node.right) > 0:          # RL case
                node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        return node

    # ── Operasi utama ──

    def insert(self, root, price):
        """Insert level harga baru — O(log n)"""
        if root is None:
            return AVLNode(price)
        if price < root.price:
            root.left  = self.insert(root.left, price)
        elif price > root.price:
            root.right = self.insert(root.right, price)
        else:
            return root   # Harga sudah ada, tidak duplikasi
        return self._balance(root)

    def search(self, root, price):
        """Cari node berdasarkan harga — O(log n)"""
        if root is None or root.price == price:
            return root
        if price < root.price:
            return self.search(root.left, price)
        return self.search(root.right, price)

    def _min_node(self, node):
        cur = node
        while cur.left:
            cur = cur.left
        return cur

    def delete(self, root, price):
        """Hapus level harga (ketika antrian kosong) — O(log n)"""
        if root is None:
            return None
        if price < root.price:
            root.left  = self.delete(root.left, price)
        elif price > root.price:
            root.right = self.delete(root.right, price)
        else:
            if root.left is None:
                return root.right
            if root.right is None:
                return root.left
            successor        = self._min_node(root.right)
            root.price       = successor.price
            root.queue       = successor.queue
            root.right       = self.delete(root.right, successor.price)
        return self._balance(root)

    def inorder(self, root, result=None):
        """Traversal inorder → harga terurut ascending — O(n)"""
        if result is None:
            result = []
        if root:
            self.inorder(root.left, result)
            result.append(root)
            self.inorder(root.right, result)
        return result

    def inorder_desc(self, root, result=None):
        """Traversal inorder terbalik → harga terurut descending — O(n)"""
        if result is None:
            result = []
        if root:
            self.inorder_desc(root.right, result)
            result.append(root)
            self.inorder_desc(root.left, result)
        return result

    def best_bid(self, root):
        """Harga beli tertinggi = node paling kanan — O(log n)"""
        if root is None:
            return None
        cur = root
        while cur.right:
            cur = cur.right
        return cur

    def best_ask(self, root):
        """Harga jual terendah = node paling kiri — O(log n)"""
        if root is None:
            return None
        cur = root
        while cur.left:
            cur = cur.left
        return cur

# ORDER BOOK — Gabungan dua AVL Tree
class OrderBook:
    """
    Order Book pasar:
    - bid_tree : AVL Tree untuk pesanan beli
    - ask_tree : AVL Tree untuk pesanan jual
    """
    def __init__(self, symbol):
        self.symbol     = symbol
        self.avl        = AVLTree()
        self.bid_root   = None
        self.ask_root   = None
        self.order_ctr  = 0
        self.trade_log  = []   # Riwayat transaksi

    def _next_id(self):
        self.order_ctr += 1
        return f"ORD{self.order_ctr:04d}"

    # ── Place Order ──

    def place_order(self, side, price, trader, qty):
        """
        Masukkan order baru.
        side: 'BUY' atau 'SELL'
        Lakukan matching terlebih dahulu, sisanya masuk antrian.
        """
        oid    = self._next_id()
        ts     = time.strftime("%H:%M:%S")
        print(f"\n  >> [{ts}] {oid} | {side} {qty} lot @ {price:,} | Trader: {trader}")

        if side == 'BUY':
            qty = self._match_buy(oid, trader, price, qty, ts)
            if qty > 0:
                self.bid_root = self.avl.insert(self.bid_root, price)
                node = self.avl.search(self.bid_root, price)
                node.queue.enqueue(oid, trader, qty)
                print(f"     Sisa {qty} lot masuk antrian BID @ {price:,}")
        else:
            qty = self._match_sell(oid, trader, price, qty, ts)
            if qty > 0:
                self.ask_root = self.avl.insert(self.ask_root, price)
                node = self.avl.search(self.ask_root, price)
                node.queue.enqueue(oid, trader, qty)
                print(f"     Sisa {qty} lot masuk antrian ASK @ {price:,}")

    # ── Matching Logic ──

    def _match_buy(self, oid, buyer, price, qty, ts):
        """
        Cocokkan order BUY dengan ASK terbaik (harga terendah).
        Eksekusi selama harga ask <= harga bid.
        """
        while qty > 0:
            best = self.avl.best_ask(self.ask_root)
            if best is None or best.price > price:
                break
            while qty > 0 and not best.queue.is_empty():
                seller_node = best.queue.peek()
                traded = min(qty, seller_node.qty)
                qty              -= traded
                seller_node.qty  -= traded
                self._record_trade(ts, buyer, seller_node.trader, best.price, traded)
                if seller_node.qty == 0:
                    best.queue.dequeue()
            if best.queue.is_empty():
                self.ask_root = self.avl.delete(self.ask_root, best.price)
        return qty

    def _match_sell(self, oid, seller, price, qty, ts):
        """
        Cocokkan order SELL dengan BID terbaik (harga tertinggi).
        Eksekusi selama harga bid >= harga ask.
        """
        while qty > 0:
            best = self.avl.best_bid(self.bid_root)
            if best is None or best.price < price:
                break
            while qty > 0 and not best.queue.is_empty():
                buyer_node = best.queue.peek()
                traded = min(qty, buyer_node.qty)
                qty             -= traded
                buyer_node.qty  -= traded
                self._record_trade(ts, buyer_node.trader, seller, best.price, traded)
                if buyer_node.qty == 0:
                    best.queue.dequeue()
            if best.queue.is_empty():
                self.bid_root = self.avl.delete(self.bid_root, best.price)
        return qty

    def _record_trade(self, ts, buyer, seller, price, qty):
        self.trade_log.append((ts, buyer, seller, price, qty))
        print(f"     ✓ MATCH: {buyer} BELI dari {seller} | {qty} lot @ {price:,}")

    # ── Cancel Order ──

    def cancel_order(self, side, price, order_id):
        """Batalkan order dari antrian berdasarkan ID"""
        if side == 'BUY':
            node = self.avl.search(self.bid_root, price)
        else:
            node = self.avl.search(self.ask_root, price)

        if node and node.queue.remove_by_id(order_id):
            print(f"  >> Order {order_id} berhasil dibatalkan.")
            if node.queue.is_empty():
                if side == 'BUY':
                    self.bid_root = self.avl.delete(self.bid_root, price)
                else:
                    self.ask_root = self.avl.delete(self.ask_root, price)
        else:
            print(f"  >> Order {order_id} tidak ditemukan.")

    # ── Tampilan ──

    def show_book(self, depth=5):
        """Tampilkan order book (ASK di atas, BID di bawah)"""
        W = 52
        print(f"\n{'─'*W}")
        print(f"  ORDER BOOK — {self.symbol}".center(W))
        print(f"{'─'*W}")

        # ASK (terurut descending agar ASK terbawah paling dekat BID)
        asks = self.avl.inorder_desc(self.ask_root)[:depth]
        if asks:
            print(f"  {'HARGA':>10}  {'LOT':>6}  {'ORDER':>5}  SIDE")
            for n in asks:
                total_qty = sum(o[2] for o in n.queue.to_list())
                print(f"  {n.price:>10,}  {total_qty:>6}  {n.queue.size:>5}  ASK")
        else:
            print("  (tidak ada ASK)")

        print(f"  {'─'*48}")

        # BID (terurut descending, BID tertinggi di atas)
        bids = self.avl.inorder_desc(self.bid_root)[:depth]
        if bids:
            print(f"  {'HARGA':>10}  {'LOT':>6}  {'ORDER':>5}  SIDE")
            for n in bids:
                total_qty = sum(o[2] for o in n.queue.to_list())
                print(f"  {n.price:>10,}  {total_qty:>6}  {n.queue.size:>5}  BID")
        else:
            print("  (tidak ada BID)")

        print(f"{'─'*W}")

    def show_queue(self, side, price):
        """Tampilkan antrian DLL pada harga tertentu"""
        if side == 'BUY':
            node = self.avl.search(self.bid_root, price)
        else:
            node = self.avl.search(self.ask_root, price)

        if node is None:
            print(f"  Tidak ada level harga {price:,} pada sisi {side}.")
            return

        print(f"\n  Antrian {side} @ {price:,} (FIFO):")
        print(f"  {'NO':>3}  {'ORDER_ID':>8}  {'TRADER':>12}  {'LOT':>6}")
        for i, (oid, trader, qty) in enumerate(node.queue.to_list(), 1):
            print(f"  {i:>3}  {oid:>8}  {trader:>12}  {qty:>6}")

    def show_trades(self, last=10):
        """Tampilkan riwayat transaksi terakhir"""
        print(f"\n  RIWAYAT TRANSAKSI (terakhir {last})")
        print(f"  {'WAKTU':>8}  {'BUYER':>12}  {'SELLER':>12}  {'HARGA':>10}  {'LOT':>6}")
        for t in self.trade_log[-last:]:
            print(f"  {t[0]:>8}  {t[1]:>12}  {t[2]:>12}  {t[3]:>10,}  {t[4]:>6}")
        if not self.trade_log:
            print("  (belum ada transaksi)")

# ANTARMUKA KONSOL — Menu utama
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def header(book):
    print(f"\n{'═'*52}")
    print(f"  MY-SIMUBURSA  |  Saham: {book.symbol}")
    print(f"  Total Transaksi: {len(book.trade_log)} trade")
    print(f"{'═'*52}")

def get_int(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("  [!] Masukkan angka yang valid.")

def main():
    clear()
    print("╔══════════════════════════════╗")
    print("║         MY-SIMUBURSA         ║")
    print("╚══════════════════════════════╝")
    symbol = input("\n  Kode saham (contoh: BBCA): ").upper() or "BBCA"
    book   = OrderBook(symbol)

    while True:
        header(book)
        print("  [1] Place Order BUY")
        print("  [2] Place Order SELL")
        print("  [3] Lihat Order Book")
        print("  [4] Lihat Antrian di Harga Tertentu")
        print("  [5] Batalkan Order")
        print("  [6] Riwayat Transaksi")
        print("  [0] Keluar")
        print(f"{'─'*52}")
        pilihan = input("  Pilih menu: ").strip()

        if pilihan == '1':
            print("\n  --- PLACE ORDER BUY ---")
            trader = input("  Nama trader  : ").strip() or "Trader"
            price  = get_int("  Harga       : ")
            qty    = get_int("  Jumlah lot  : ")
            book.place_order('BUY', price, trader, qty)
            input("\n  [Enter] lanjut...")

        elif pilihan == '2':
            print("\n  --- PLACE ORDER SELL ---")
            trader = input("  Nama trader  : ").strip() or "Trader"
            price  = get_int("  Harga       : ")
            qty    = get_int("  Jumlah lot  : ")
            book.place_order('SELL', price, trader, qty)
            input("\n  [Enter] lanjut...")

        elif pilihan == '3':
            depth = get_int("\n  Tampilkan berapa level harga? (5): ") or 5
            book.show_book(depth)
            input("\n  [Enter] lanjut...")

        elif pilihan == '4':
            side  = input("\n  Sisi (BUY/SELL): ").upper()
            price = get_int("  Harga: ")
            book.show_queue(side, price)
            input("\n  [Enter] lanjut...")

        elif pilihan == '5':
            side     = input("\n  Sisi order (BUY/SELL): ").upper()
            price    = get_int("  Harga order: ")
            order_id = input("  ID order (contoh ORD0001): ").strip().upper()
            book.cancel_order(side, price, order_id)
            input("\n  [Enter] lanjut...")

        elif pilihan == '6':
            book.show_trades()
            input("\n  [Enter] lanjut...")

        elif pilihan == '0':
            print("\n  Terima kasih. My-Simubursa ditutup.\n")
            break

        else:
            print("  [!] Pilihan tidak valid.")

if __name__ == "__main__":
    main()