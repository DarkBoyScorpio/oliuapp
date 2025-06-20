gia_mat_hang = {
    "MÍT 500G": 115000,
    "THẬP CẨM 500G": 80000,
    "CHUỐI SẤY MỘC 250G": 35000,
    "CHUỐI SẤY MỘC 500G": 65000,
    "KHOAI TÂY RONG BIỂN 250G": 95000,
    "KHOAI TÂY RONG BIỂN 500G": 180000,
    "KHOAI TÂY MẮM 250G": 95000,
    "KHOAI TÂY MẮM 500G": 180000,
    "KHOAI MÔN TRỨNG CUA 250G": 90000,
    "KHOAI MÔN TRỨNG CUA 500G": 170000,
    "NẾP CHÁY CHÀ BÔNG 150G x3": 50000,
    "NẾP CHÁY CHÀ BÔNG 150G x5": 80000,
    "CƠM CHÁY CHÀ BÔNG 200G": 50000,
    "GẠO LỨT RONG BIỂN 200G": 55000,
    "BÁNH TRÁNG MẮM": 35000,
    "MẬT ONG 500ML": 120000,
    "MẬT ONG 1 LÍT": 215000,
    "MẮM 1 LÍT": 80000,
    "ĐIỀU RANG MUỐI 200G": 65000,
    "ĐIỀU RANG MUỐI 500G": 160000,
    "ĐIỀU MẮM ỚT 500G": 180000
}


product_column_map = {
    "Mít 500g": 16,
    "Thập cẩm 500g": 17,
    "Chuối mộc 250g": 18,
    "Chuối mộc 500g": 19,
    "Khoai tây rong biển 250g": 20,
    "Khoai tây rong biển 500g": 21,
    "Khoai tây mắm 250g": 22,
    "Khoai tây mắm 500g": 23,
    "Khoai môn trứng cua 250g": 24,
    "Khoai môn trứng cua 500g": 25,
    "Nếp cháy chà bông x3": 26,
    "Nếp cháy chà bông x5": 27,
    "Cơm cháy chà bông 200g": 28,
    "Gạo lứt rong biển 200g": 29,
    "Bánh tráng mắm": 30,
    "Mật ong 500ml": 31,
    "Mật ong 1 lít": 32,
    "Mắm 1 lít": 33,
    "Điều rang muối 200g": 34,
    "Điều rang muối 500g": 35,
    "Điều mắm ớt 500g": 36,
}

kho_nhan_hang=["Q8 - Bến Bình Đông", "Chu Văn An - Bình Thạnh"]
hinh_thuc_nhan_hang = ["Nhận hàng trực tiếp tại kho", "Nhờ shop đặt ship"]
thoi_gian_nhan_hang = [
                        "",
                        "Ship chiều thứ 7", 
                        "Ship trưa chiều CN", 
                        "Sau 19g thứ 2", 
                        "Sau 19g thứ 3"
                        "Sau 19g thứ 4"
                        ]


TARGET_SALES = 200_000_000
SCOPE=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]


STK = "TINHNGUYENOLIU"
TEN_CHU_TK = "NGUYEN THI NGOC TRAM"
BIN_BANK = "970422"

MEO_HTML = """
<!-- Mèo chạy -->
<div id="neko-container" style="position: fixed; bottom: 0; left: 0; font-size: 35px; z-index: 9999;">
  <div id="hover-text" style="
    display: none;
    font-size: 12px;
    color: white;
    background: rgba(0, 0, 0, 0.6);
    padding: 4px 10px;
    border-radius: 15px;
    margin-bottom: 2px;
    text-align: center;
    width: max-content;
    max-width: 150px;
    position: relative;
    left: 50%;
    transform: translateX(-50%);
    box-shadow: 0 0 6px rgba(0,0,0,0.4);
  ">
    Xê raaaaaaa
  </div>
  <div id="neko">🐈</div>
</div>

<!-- 💨 Xì hơi -->
<div id="trail" style="position: fixed; bottom: 0; left: 0; font-size: 30px; display: none; z-index: 9998;">
  💨
</div>

<script>
let nekoContainer = document.getElementById("neko-container");
let neko = document.getElementById("neko");
let hoverText = document.getElementById("hover-text");
let trail = document.getElementById("trail");

let pos = window.innerWidth;
let speed = 1.5;
let boosted = false;

// Di chuyển mèo
function moveCat() {
  pos -= speed;
  if (pos < -50) {
    pos = window.innerWidth + 50;
  }
  nekoContainer.style.left = pos + "px";

  if (boosted && speed > 1.5) {
    speed -= 0.05;
    if (speed <= 1.5) {
      speed = 1.5;
      boosted = false;
    }
  }

  requestAnimationFrame(moveCat);
}
moveCat();

// 💨 xì hơi định kỳ
setInterval(() => {
  trail.style.left = (pos + 40) + "px";
  trail.style.display = "block";
  setTimeout(() => {
    trail.style.display = "none";
  }, 400);

  speed = 4;
  boosted = true;
}, 2000);

// Hover: hiện thinking + đổi mèo tím
nekoContainer.addEventListener("mouseover", () => {
  hoverText.style.display = "block";
  neko.innerText = "🐈‍⬛";
});
nekoContainer.addEventListener("mouseout", () => {
  hoverText.style.display = "none";
  neko.innerText = "🐈";
});
</script>
"""