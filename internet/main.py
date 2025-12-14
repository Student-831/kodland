from flask import Flask, jsonify, render_template_string, request
import random

app = Flask(__name__)


@app.route('/rastgele')
def hello_world():
        facts_list = [
                "Teknolojik bağımlılıktan mustarip olan çoğu kişi, kendilerini şebeke kapsama alanı dışında bulduklarında veya cihazlarını kullanamadıkları zaman yoğun stres yaşarlar.",
                "2018 yılında yapılan bir araştırmaya göre 18-34 yaş arası kişilerin %50'den fazlası kendilerini akıllı telefonlarına bağımlı olarak görüyor.",
                "Teknolojik bağımlılık çalışması, modern bilimsel araştırmanın en ilgili alanlarından biridir.",
                "2019'da yapılan bir araştırmaya göre, insanların %60'ından fazlası akıllı telefonlarındaki iş mesajlarına işten ayrıldıktan sonraki 15 dakika içinde yanıt veriyor.",
                "Teknolojik bağımlılıkla mücadele etmenin bir yolu, zevk veren ve ruh halini iyileştiren faaliyetler aramaktır.",
                "Elon Musk, sosyal ağların içeriği görüntülemek için mümkün olduğunca fazla zaman harcamamız için bizi platformun içinde tutmak üzere tasarlandığını iddia ediyor.",
                "Elon Musk ayrıca sosyal ağların düzenlenmesini ve kullanıcıların kişisel verilerinin korunmasını savunmaktadır. Sosyal ağların hakkımızda büyük miktarda bilgi topladığını ve bu bilgilerin daha sonra düşüncelerimizi ve davranışlarımızı manipüle etmek için kullanılabileceğini iddia ediyor.",
                "Sosyal ağların olumlu ve olumsuz yanları vardır ve bu platformları kullanırken her ikisinin de farkında olmalıyız."
        ]
        return f'<h1>{random.choice(facts_list)}</h1>'


@app.route('/')
def home():
        return "<h1>ekleme yapmanız gerekli</h1><a href='/rastgele'>rastgele hadi</a> <a href='/game'>oyun oynayalım</a>"


@app.route('/game')
def game():
        html = '''
        <!doctype html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Mayın Tarlası</title>
            <style>
                body { font-family: monospace; }
                #board { display: inline-block; line-height: 1.6; }
                .row { display: block; }
                .cell { display: inline-block; width: 34px; height: 28px; text-align: center; vertical-align: middle; cursor: pointer; }
                button { margin: 8px 0; }
            </style>
        </head>
        <body>
            <h2>Mayın Tarlası - 10x10, 15 bomba</h2>
            <div>
                <button id="restart">Yeniden Başlat</button>
                <span id="status"></span>
            </div>
            <div id="board"></div>

            <script>
                let size = 10;
                let bombsCount = 15;
                let bombs = [];
                let revealed = [];
                let flagged = [];
                let counts = [];
                let gameOver = false;

                async function newGame(){
                    const res = await fetch('/game/new');
                    const data = await res.json();
                    size = data.size;
                    bombs = data.bombs.map(x=>[x[0], x[1]]);
                    bombsCount = data.total;
                    revealed = Array.from({length:size}, ()=>Array.from({length:size}, ()=>false));
                    flagged = Array.from({length:size}, ()=>Array.from({length:size}, ()=>false));
                    counts = Array.from({length:size}, ()=>Array(size).fill(0));
                    gameOver = false;
                    document.getElementById('status').textContent='';
                    computeCounts();
                    renderBoard();
                }

                function computeCounts(){
                    // reset counts
                    for(let r=0;r<size;r++) for(let c=0;c<size;c++) counts[r][c]=0;
                    // for each bomb, increment neighbors' counts
                    for(const [br,bc] of bombs){
                        // mark bomb cell as -1 (optional)
                        counts[br][bc] = -1;
                        for(let dr=-1;dr<=1;dr++){
                            for(let dc=-1;dc<=1;dc++){
                                if(dr===0 && dc===0) continue;
                                const nr = br+dr, nc = bc+dc;
                                if(nr>=0 && nr<size && nc>=0 && nc<size){
                                    if(counts[nr][nc] !== -1) counts[nr][nc]++;
                                }
                            }
                        }
                    }
                }

                function renderBoard(){
                    const board = document.getElementById('board');
                    board.innerHTML='';
                    for(let r=0;r<size;r++){
                        const row = document.createElement('div'); row.className='row';
                        for(let c=0;c<size;c++){
                            const cell = document.createElement('span'); cell.className='cell';
                            cell.dataset.r = r; cell.dataset.c = c;
                            updateCellElement(cell,r,c);
                            cell.addEventListener('click', (e)=>{ if(!gameOver) revealCell(r,c); });
                            cell.addEventListener('contextmenu', (e)=>{ e.preventDefault(); if(!gameOver) toggleFlag(r,c); });
                            row.appendChild(cell);
                        }
                        board.appendChild(row);
                    }
                }

                function updateCellElement(el,r,c){
                    if(revealed[r][c]){
                        if(bombs.some(b=>b[0]===r && b[1]===c)){
                            el.textContent = '[M]';
                            el.style.background = '#faa';
                        } else {
                            const v = counts[r][c];
                            el.textContent = '[' + (v===0? '0': v) + ']';
                            el.style.background = '#efe';
                        }
                        el.style.cursor='default';
                    } else {
                        if(flagged[r][c]){ el.textContent='[B]'; el.style.background='#ffd'; }
                        else { el.textContent='[ ]'; el.style.background=''; }
                        el.style.cursor='pointer';
                    }
                }

                function revealCell(r,c){
                    if(revealed[r][c] || flagged[r][c]) return;
                    revealed[r][c]=true;
                    if(bombs.some(b=>b[0]===r && b[1]===c)){
                        // hit a bomb
                        revealAllBombs();
                        document.getElementById('status').textContent=' Patladınız! Oyunu yeniden başlatın.';
                        gameOver = true;
                        renderBoard();
                        return;
                    }
                    if(counts[r][c]===0){
                        // flood fill
                        for(let dr=-1;dr<=1;dr++) for(let dc=-1;dc<=1;dc++){
                            const nr=r+dr, nc=c+dc;
                            if(nr>=0 && nr<size && nc>=0 && nc<size){
                                if(!revealed[nr][nc]) revealCell(nr,nc);
                            }
                        }
                    }
                    renderBoard();
                    checkWin();
                }

                function toggleFlag(r,c){
                    if(revealed[r][c]) return;
                    flagged[r][c] = !flagged[r][c];
                    renderBoard();
                }

                function revealAllBombs(){
                    for(const [r,c] of bombs) revealed[r][c]=true;
                }

                function checkWin(){
                    let unrevealedCount=0;
                    for(let r=0;r<size;r++) for(let c=0;c<size;c++) if(!revealed[r][c]) unrevealedCount++;
                    if(unrevealedCount === bombsCount){
                        document.getElementById('status').textContent=' Kazandınız! Tebrikler.';
                        gameOver = true;
                        revealAllBombs();
                        renderBoard();
                    }
                }

                document.getElementById('restart').addEventListener('click', ()=> newGame());

                // start
                newGame();
            </script>
        </body>
        </html>
        '''
        return render_template_string(html)


@app.route('/game/new')
def game_new():
        size = 10
        bombs = 15
        positions = set()
        while len(positions) < bombs:
                r = random.randrange(size)
                c = random.randrange(size)
                positions.add((r,c))
        bombs_list = [[r,c] for (r,c) in positions]
        return jsonify({'size': size, 'bombs': bombs_list, 'total': bombs})


if __name__ == '__main__':
        app.run(debug=True)
