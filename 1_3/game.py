# minesweeper_game.py

import random

class MinesweeperGame:
    """8x8 Mayın Tarlası Oyununun tüm mantığını yönetir."""
    
    BOARD_SIZE = 8
    
    # Koordinat haritalama: 'a' -> 0, 'h' -> 7
    Y_COORDS = {chr(97 + i): i for i in range(BOARD_SIZE)} # {'a': 0, 'b': 1, ...}
    
    # Görsel karakterler
    CLOSED = '[]'
    EMPTY_OPEN = '[ ]'
    FLAG = '[B]'
    MINE = '[M]'
    
    def __init__(self, num_mines):
        self.num_mines = num_mines
        self.is_playing = True
        self.game_won = False
        
        # Arka plan tahtaları
        # mine_board: -1 (mayın), 0-8 (komşu mayın sayısı)
        self.mine_board = [[0] * self.BOARD_SIZE for _ in range(self.BOARD_SIZE)]
        # display_board: Kullanıcının gördüğü tahta (CLOSED, FLAG, EMPTY_OPEN, '1', '2'...)
        self.display_board = [[self.CLOSED] * self.BOARD_SIZE for _ in range(self.BOARD_SIZE)]
        
        self.place_mines_and_calculate_neighbors()

    def place_mines_and_calculate_neighbors(self):
        # Mayınları rastgele yerleştirir ve komşu sayılarını hesaplar.
        mines_placed = 0
        while mines_placed < self.num_mines:
            row = random.randint(0, self.BOARD_SIZE - 1)
            col = random.randint(0, self.BOARD_SIZE - 1)
            
            # Eğer o karede zaten mayın yoksa
            if self.mine_board[row][col] != -1:
                self.mine_board[row][col] = -1  # Mayın yerleştir
                mines_placed += 1
                
                # Komşu mayın sayılarını güncelle
                for r in range(max(0, row-1), min(self.BOARD_SIZE, row+2)):
                    for c in range(max(0, col-1), min(self.BOARD_SIZE, col+2)):
                        if self.mine_board[r][c] != -1:
                            self.mine_board[r][c] += 1

    def get_board_display(self, show_all=False):
        """Mevcut tahta durumunu Discord'da gösterilecek formatta döndürür."""
        
        # Başlık ve sütun numaraları
        header = "    " + " ".join(f"{i:2}" for i in range(1, self.BOARD_SIZE + 1))
        separator = "  " + "-" * (self.BOARD_SIZE * 3 + 1)
        
        board_lines = [header, separator]
        
        for r in range(self.BOARD_SIZE):
            y_coord = chr(97 + r) # 'a', 'b', ...
            row_display = [y_coord + " |"]
            
            for c in range(self.BOARD_SIZE):
                cell = self.display_board[r][c]
                
                # Oyun bittiyse ve tüm mayınları göstermek gerekiyorsa
                if show_all and self.mine_board[r][c] == -1 and cell != self.FLAG:
                    cell = self.MINE # Mayın olan ama bayrak dikilmeyen yer
                
                row_display.append(cell)
            
            board_lines.append(" ".join(row_display))
            
        # Monospace font için üç tırnak içine alınmış kod bloğu olarak döndür
        return "\n".join(board_lines)

    def is_valid_input(self, x, y):
        """Koordinatların tahta sınırları içinde olup olmadığını kontrol eder."""
        return 0 <= x < self.BOARD_SIZE and 0 <= y < self.BOARD_SIZE

    def coordinate_to_index(self, x_str, y_str):
        """'K2b' -> (row=1, col=1) indekslerine çevirir."""
        try:
            col = int(x_str) - 1 # X (Sütun) 1'den başlar
            row = self.Y_COORDS.get(y_str.lower()) # Y (Satır) 'a'dan başlar
            if row is None or not self.is_valid_input(col, row):
                return None, None
            return row, col
        except ValueError:
            return None, None
            
    def check_win(self):
        """Oyunun kazanılıp kazanılmadığını kontrol eder."""
        # Tüm mayınsız kareler açıldıysa oyun kazanılmıştır.
        closed_safe_cells = 0
        for r in range(self.BOARD_SIZE):
            for c in range(self.BOARD_SIZE):
                # Mayın değilse ve kapalıysa (Bayrak da kapalı sayılır)
                if self.mine_board[r][c] != -1 and self.display_board[r][c] in [self.CLOSED, self.FLAG]:
                    closed_safe_cells += 1
        
        if closed_safe_cells == 0:
            self.game_won = True
            self.is_playing = False
            return True
        return False
        
    def reveal_cell(self, r, c):
        """Belirtilen kareyi açar. Etrafı boşsa yayılarak açar (recursive)."""
        if not self.is_valid_input(c, r) or self.display_board[r][c] != self.CLOSED:
            return
            
        # Mayın mı?
        if self.mine_board[r][c] == -1:
            self.is_playing = False
            return # Oyuncu kaybetti
        
        # Komşu mayın sayısı kaç?
        count = self.mine_board[r][c]
        if count > 0:
            self.display_board[r][c] = f'[{count}]'
        else:
            # Komşu mayın yoksa (Boş kare)
            self.display_board[r][c] = self.EMPTY_OPEN
            
            # Etrafındaki kareleri otomatik aç
            for row_offset in range(-1, 2):
                for col_offset in range(-1, 2):
                    self.reveal_cell(r + row_offset, c + col_offset)

    def handle_action(self, action_type, x_str, y_str):
        """Kullanıcıdan gelen komutu işler (K veya B)."""
        
        r, c = self.coordinate_to_index(x_str, y_str)
        if r is None:
            return "Hata: Geçersiz koordinat. Örn: K2b"

        current_cell = self.display_board[r][c]

        if action_type == 'K': # Kazma (Reveal)
            if current_cell != self.CLOSED and current_cell != self.FLAG:
                return "Hata: Bu kare zaten açık."
            
            if current_cell == self.FLAG:
                return "Hata: Önce bayrağı kaldırın (B ile bayrak kaldırabilirsiniz)."

            self.reveal_cell(r, c)
            
            if not self.is_playing and not self.game_won:
                return "KAYBETTİNİZ! 💥 Mayına bastınız!"
            
            if self.check_win():
                return "TEBRİKLER! 🎉 Tüm mayınsız alanları açtınız ve oyunu kazandınız!"

        elif action_type == 'B': # Bayrak (Flag)
            if current_cell == self.CLOSED:
                self.display_board[r][c] = self.FLAG
                return "Bayrak dikildi."
            elif current_cell == self.FLAG:
                self.display_board[r][c] = self.CLOSED
                return "Bayrak kaldırıldı."
            else:
                return "Hata: Açık bir alana bayrak dikemezsiniz."
        
        return "İşlem başarılı." # Başarılı bir K veya B işleminden sonra