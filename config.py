GIA_ROW_VALUE = 3
GIA_ROW_NAME = 4
GIA_ROW_START = 14
GIA_ROW_END = 32

HANG_TON_NAME_START = "B3"
HANG_TON_NAME_END = "B19"
HANG_TON_VALUE_START = "Q3"
HANG_TON_VALUE_END = "Q19"

SHEET_HANG_TON_NAME = "Quản lí tồn"

TIEN_BAN_HANG = "TIỀN BÁN HÀNG (2)"

MENU_TREE = ["📥 Nhập đơn hàng", "📄 Tra cứu đơn hàng", "🖨️ In đơn hàng", "📊 Con số biết nói", "👉 Về chúng tôi"]

MIT_500G = "MÍT 500G"
THAP_CAM_500G = "THẬP CẨM 500G"
CHUOI_SAY_ME_DUONG_500G = "CHUỐI SẤY MÈ ĐƯỜNG 500G"
CHUOI_SAY_MOC_500G = "CHUỐI SẤY MỘC 500G"
KHOAI_TAY_RONG_BIEN_250G = "KHOAI TÂY RONG BIỂN 250G"
KHOAI_TAY_MAM_250G = "KHOAI TÂY MẮM 250G"
KHOAI_MON_TRUNG_CUA_250G = "KHOAI MÔN TRỨNG CUA 250G"
NEP_CHAY_CHA_BONG_150G_X3 = "NẾP CHÁY CHÀ BÔNG 150G x3"
NEP_CHAY_CHA_BONG_150G_X5 = "NẾP CHÁY CHÀ BÔNG 150G x5"
COM_CHAY_CHA_BONG_200G = "CƠM CHÁY CHÀ BÔNG 200G"
GAO_LUT_RONG_BIEN_200G = "GẠO LỨT RONG BIỂN 200G"
BANH_TRANG_MAM = "BÁNH TRÁNG MẮM"
MAT_ONG_500ML = "MẬT ONG 500ML"
MAT_ONG_1_LIT = "MẬT ONG 1 LÍT"
MAM_1_LIT = "MẮM 1 LÍT"
DIEU_RANG_MUOI_200G = "ĐIỀU RANG MUỐI 200G"
DIEU_RANG_MUOI_500G = "ĐIỀU RANG MUỐI 500G"
DIEU_MAM_OT_500G = "ĐIỀU MẮM ỚT 500G"


product_column_map = {
    MIT_500G: 15,
    THAP_CAM_500G: 16,
    CHUOI_SAY_ME_DUONG_500G: 17,
    CHUOI_SAY_MOC_500G: 18,
    KHOAI_TAY_RONG_BIEN_250G: 19,
    KHOAI_TAY_MAM_250G: 20,
    KHOAI_MON_TRUNG_CUA_250G: 21,
    NEP_CHAY_CHA_BONG_150G_X3: 22,
    NEP_CHAY_CHA_BONG_150G_X5: 23,
    COM_CHAY_CHA_BONG_200G: 24,
    GAO_LUT_RONG_BIEN_200G: 25,
    BANH_TRANG_MAM: 26,
    MAT_ONG_500ML: 27,
    MAT_ONG_1_LIT: 28,
    MAM_1_LIT: 29,
    DIEU_RANG_MUOI_200G: 30,
    DIEU_RANG_MUOI_500G: 31,
    DIEU_MAM_OT_500G: 32,
}

thoi_gian_nhan_hang = [
                        "",
                        "Nhận trực tiếp - Trưa thứ 7", 
                        "Bookship - Chiều thứ 7", 
                        "Bookship - Chủ nhật", 
                        ]


TARGET_SALES = 200_000_000
SCOPE=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]


STK = "2845"
TEN_CHU_TK = "PHAM THI CAM TU"
BIN_BANK = "970422"

MEO_HTML = """
<!-- Mèo chạy trước -->
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
    position: relative;
    left: 50%;
    transform: translateX(-50%);
  ">
    Xê raaaaaaa
  </div>
  <div id="neko">🐈</div>
</div>

<!-- Chó chạy sau -->
<div id="dog-container" style="position: fixed; bottom: 0; left: 0; font-size: 35px; z-index: 9998;">
  <div id="dog-hover-text" style="
    display: none;
    font-size: 12px;
    color: white;
    background: rgba(0, 0, 0, 0.6);
    padding: 4px 10px;
    border-radius: 15px;
    margin-bottom: 2px;
    text-align: center;
    position: relative;
    left: 50%;
    transform: translateX(-50%);
  ">
    Gâu gâu!
  </div>
  <div id="dog">🐕</div>
</div>

<!-- 💨 Xì hơi mèo -->
<div id="cat-trail" style="position: fixed; bottom: 0; left: 0; font-size: 30px; display: none; z-index: 9996;">
  💨
</div>

<script>
let nekoContainer = document.getElementById("neko-container");
let neko = document.getElementById("neko");
let hoverText = document.getElementById("hover-text");

let dogContainer = document.getElementById("dog-container");
let dog = document.getElementById("dog");
let dogHoverText = document.getElementById("dog-hover-text");
let catTrail = document.getElementById("cat-trail");

// mèo trước, chó sau
let catPos = window.innerWidth;
let dogPos = catPos + 140;

let catSpeed = 2.3;
let baseDogSpeed = 3.2;
let dogSpeed = baseDogSpeed;

let dogOffset = 0;
let fartCooldown = false;

function catFart() {
  if (fartCooldown) return;

  fartCooldown = true;

  // khói
  catTrail.style.left = (catPos + 15) + "px";
  catTrail.style.display = "block";

  // chó té ngửa
  dogContainer.style.transform = "rotate(90deg)";
  dogOffset = 80;

  setTimeout(() => {
    catTrail.style.display = "none";
    dogContainer.style.transform = "rotate(0deg)";
    fartCooldown = false;
  }, 600);
}

function moveAnimals() {
  catPos -= catSpeed;

  // chó đuổi mèo
  if (!fartCooldown) {
    dogPos -= dogSpeed;
  }

  // chó bị đẩy lùi
  if (dogOffset > 0) {
    dogOffset -= 0.8;
    if (dogOffset < 0) dogOffset = 0;
  }

  // khoảng cách
  let distance = dogPos - catPos;

  // nếu chó tới gần → mèo xì hơi
  if (distance < 80 && !fartCooldown) {
    catFart();
  }

  // reset khi ra khỏi màn hình
  if (catPos < -60) {
    catPos = window.innerWidth + 40;
    dogPos = catPos + 140;
  }

  nekoContainer.style.left = catPos + "px";
  dogContainer.style.left = (dogPos + dogOffset) + "px";

  requestAnimationFrame(moveAnimals);
}
moveAnimals();

// Hover mèo: hiện chữ + đổi mèo tím + chó chạy chậm
nekoContainer.addEventListener("mouseover", () => {
  hoverText.style.display = "block";
  neko.innerText = "🐈‍⬛";
  dogSpeed = 1.0; // chạy chậm
});
nekoContainer.addEventListener("mouseout", () => {
  hoverText.style.display = "none";
  neko.innerText = "🐈";
  dogSpeed = baseDogSpeed; // về tốc độ bình thường
});

// Click mèo → xì hơi ngay
nekoContainer.addEventListener("click", () => {
  catFart();
});

// Hover chó
dogContainer.addEventListener("mouseover", () => {
  dogHoverText.style.display = "block";
  dog.innerText = "🐕‍🦺";
});
dogContainer.addEventListener("mouseout", () => {
  dogHoverText.style.display = "none";
  dog.innerText = "🐕";
});

// Double click chó → tăng tốc
dogContainer.addEventListener("click", () => {
  dogSpeed = 4.5;
  setTimeout(() => {
    dogSpeed = baseDogSpeed;
  }, 2000);
});
</script>

"""

PROGRESS_BAR_HTML = """
    <div style="position: relative; background-color: #e0e0e0; height: 24px; border-radius: 12px; overflow: hidden; margin-top: 10px; margin-bottom: 10px;">
        <div style="
            width: {percent}%;
            background-color: #4B8BBE;
            height: 100%;
            transition: width 0.5s;
        "></div>
        <div style="
            position: absolute;
            top: 0;
            left: calc({percent}% - 20px);
            height: 100%;
            width: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
        ">
            🚀
        </div>
    </div>
    """

PRINT_HTML = """
      <div id="print-area" style="display:none;">
          <h3>📌 Thông tin khách hàng</h3>
          {customer_table}

          <h3>🛒 Mặt hàng đã đặt</h3>
          {order_table}
      </div>

      <button id="printBtn" style="
          background-color:#000000; 
          color:white; 
          padding:0.4rem 0.9rem; 
          border:none; 
          border-radius:0.5rem; 
          cursor:pointer; 
          margin-top:-6px; 
          vertical-align:middle;
          font-family: 'Source Sans Pro', sans-serif; 
          font-size:1rem; 
          font-weight:400;
          line-height:1.5;
      ">
          🖨️ In đơn hàng
      </button>

      <script>
      document.getElementById("printBtn").addEventListener("click", function() {{
          const printArea = document.getElementById("print-area");
          if (!printArea) {{
              alert("Không tìm thấy nội dung để in!");
              return;
          }}
          const printWindow = window.open('', '', 'width=800,height=600');
          printWindow.document.write('<html><head><title>In đơn hàng</title>');
          printWindow.document.write('<style>');
          printWindow.document.write('body{{font-family:Arial;padding:20px;}}');
          printWindow.document.write('table{{border-collapse:collapse;width:100%;margin-top:10px;}}');
          printWindow.document.write('th,td{{border:1px solid #ccc;padding:8px;text-align:left;}}');
          printWindow.document.write('</style></head><body>');
          printWindow.document.write(printArea.innerHTML);
          printWindow.document.write('</body></html>');
          printWindow.document.close();
          printWindow.focus();
          printWindow.print();
      }});
      </script>
      """

NOTE_HTML = """
                <div style="text-align: center; font-size: 13px; color: gray;">
                    Sheet đang hiển thị chỉ có quyền xem, không thể chỉnh sửa
                </div>
                """

TIEU_DE_HTML = """
    <style>
    .hero-title {
        text-align: left;
        color: #1E3A8A;
        font-size: 3em;
        font-weight: bold;
        font-family: 'Montserrat', sans-serif;
    }
    .section-title {
        font-size: 2em;
        font-weight: 700;
        margin: 40px 0 20px;
        color: #002B5B;
    }
    </style>

    <div class="hero-title">
        <h1>Đội tình nguyện ÔLiu</h1>
    </div>
    """

GIOI_THIEU_HTML = """
    <style>
    .about-container {
        max-width: 1000px;
        margin: 0;
        padding: 20px 25px;
        border-radius: 16px;
        background: #E6F0FF; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        box-sizing: border-box;
    }

    .about-text {
        text-align: justify;
        line-height: 1.6;
        color: #002B5B;
        font-size: 1.05rem;
        word-wrap: break-word;
    }

    .about-text p {
        margin-bottom: 16px;
    }

    /* Responsive */
    @media (max-width: 768px) {
        .about-container {
            padding: 15px 15px;
        }
        .about-text {
            font-size: 0.98rem;
            line-height: 1.5;
        }
    }
    </style>

    <div class="about-container">
    <div class="about-text">
    <p><b>[Ô liu - Olympia In U]</b></p>
    <p>Mọi người đều biết đến “Đường lên đỉnh Olympia” (DLDO) là một chương trình truyền hình dành cho tất cả các bạn học sinh phổ thông trên toàn quốc, nơi thể hiện kiến thức, bản lĩnh của các nhà leo núi qua từng câu hỏi. Không chỉ thế, Olympia còn là một ngã rẽ, là cánh cửa mở ra nhiều cơ hội mới, những mối quan hệ mới cho các bạn thí sinh. Hãy để Ô liu kể bạn nghe câu chuyện của một Olympian - cách mà chúng tôi gọi các bạn tham gia DLDO.</p>
    <p>Kết thúc những trận đấu gay cấn, các bạn rời trường quay trong những cung bậc cảm xúc khác nhau, rồi bạn chợt nhận ra mình đã là một thành viên trong một đại gia đình có tên Olympians - cộng đồng các thí sinh tham gia chương trình DLDO. Olympians luôn cố gắng sẻ chia, góp sức cùng nhau tạo ra những giá trị tốt đẹp cho cuộc sống. Chúng ta gắn kết qua những ngày vui thỏa sức cùng Ono, qua những màn trình diễn ở Olym Acoustic.</p>
    <p>Với mục đích duy trì và phát triển các giá trị tốt đẹp, tinh thần lan tỏa của "nhóm máu O", đội tình nguyện Ô liu được thành lập cùng fanpage để các bạn Olympians và mọi người nói riêng có thể theo dõi, đồng hành cũng như chung tay giúp đỡ những hoàn cảnh khó khăn, góp sức trẻ tạo nên giá trị tử tế.</p>
    <p>Ô liu rất mong nhận được sự quan tâm của các bạn gần xa, nhất là những bạn không phải Olympian. Chúng ta hãy cùng nhau tạo ra giá trị khác biệt. Khi bạn cho đi, bạn chắc chắn sẽ nhận lại nhiều hơn những gì bạn đang có.</p>
    </div>
    </div>
    """

SOCIAL_HTML = """
    <style>
    .contact-container {
        max-width: 900px;
        margin: 0 auto;
        padding: 40px 25px;
        border-radius: 20px;
        background: linear-gradient(135deg, #E6F0FF, #FFFFFF);
        box-shadow: 0 8px 20px rgba(0,0,0,0.08);
        box-sizing: border-box;
        text-align: center;
    }
    .contact-text {
        font-size: 1.1rem;
        line-height: 1.8;
        color: #002B5B;
        margin-bottom: 30px;
    }
    .social-icons {
        display: flex;
        justify-content: center;
        gap: 25px;
        flex-wrap: wrap;
    }
    .social-card {
        background: #fff;
        border-radius: 16px;
        padding: 15px;
        width: 70px;
        height: 70px;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .social-card:hover {
        transform: translateY(-5px) scale(1.1);
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
    }
    .social-card svg {
        width: 32px;
        height: 32px;
        fill: #002B5B; /* màu chủ đạo */
        transition: fill 0.3s ease;
    }
    .social-card:hover svg {
        fill: #FF8C42; /* màu hover nổi bật */
    }
    </style>

    <div class="contact-container">
        <div class="contact-text">
            <b>Email:</b> tinhnguyenoliu@gmail.com<br>
            <b>Trưởng BTC - Thảo Trang:</b> 0901367931<br>
            <b>Phụ trách gây quỹ - Nhật Trình:</b> 0388534146<br>
            <b><br>
            <div class="social-icons">
                <a href="https://www.facebook.com/oliufanpage" target="_blank" class="social-card"><img src="https://cdn-icons-png.flaticon.com/512/733/733547.png"></a>
                <a href="https://www.tiktok.com/@tinhnguyenoliu" target="_blank" class="social-card"><img src="https://cdn-icons-png.flaticon.com/512/3046/3046122.png"></a>
            </div>
        </div>
    </div>
    """

SLIDER_HTML_TEMPLATE = """
<style>
.wrapper {{
    width: 100%;
    overflow: hidden;
    background: linear-gradient(to right, var(--background-color), var(--secondary-background-color));
    padding: 30px 0;
    border-radius: 20px;
    box-shadow: inset 0 0 8px rgba(0,0,0,0.05);
    position: relative;
}}

.track {{
    display: flex;
    width: max-content;
    animation: moveRight 40s linear infinite;
}}

@keyframes moveRight {{
    0%   {{ transform: translateX(-50%); }}
    100% {{ transform: translateX(0%); }}
}}

.track img {{
    height: 230px;
    width: auto;
    margin-right: 20px;
    border-radius: 16px;
    box-shadow: 0 6px 16px rgba(0,0,0,0.15);
    transition: transform 0.4s ease;
    flex-shrink: 0;
    background-color: var(--secondary-background-color);
}}

.track img:hover {{
    transform: scale(1.05);
}}
</style>

<div class="wrapper">
    <div class="track">
        {images_html}
        {images_html}
    </div>
</div>
"""

PRINT_MULTI_HTML = """
                <button onclick="printAll()" style="
                    background-color:#000;
                    color:white;
                    padding:0.5rem 1rem;
                    border:none;
                    border-radius:6px;
                    cursor:pointer;">
                    🖨️ In
                </button>

                <script>
                function printAll() {{
                    const win = window.open('', '', 'width=900,height=700');

                    win.document.write(`
                        <html>
                        <head>
                            <title>In hàng loạt</title>
                            <style>
                                body {{ font-family: Arial; padding: 20px; }}
                                table {{ border-collapse: collapse; width: 100%; margin-top: 10px; }}
                                th, td {{ border: 1px solid #ccc; padding: 8px; }}

                                .order {{
                                    page-break-after: always;
                                }}
                            </style>
                        </head>
                        <body>
                            {all_orders_html}
                        </body>
                        </html>
                    `);

                    win.document.close();

                    // 🔥 QUAN TRỌNG: chỉ print 1 lần
                    win.onload = function() {{
                        win.focus();
                        win.print();
                    }};
                }}
                </script>
                """