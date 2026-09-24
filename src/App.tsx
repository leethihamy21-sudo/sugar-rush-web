import { useEffect, useRef, useState } from 'react';

const assetPathPrefix = "/assets";

const imgRectangle1 = "/banner.jpg";
const imgRectangle2252 = "/1bb74.png";
const imgRectangle2231 = "/1789878789707_7822267878735642140_7822267878735642140_26a47450bb6e5961cf0dcc28b177ddc8.jpg";
const imgRectangle2233 = "/1789878789714_7822267878735642140_7822267878735642140_7f662cb53b21442292cb4252d1ca924e.jpg";
const imgFrame1000004408 = "/1789878789699_7822267878735642140_7822267878735642140_294ecdc0c525dd674b514b4402bcd34d.jpg";
const imgFrame1000004406 = "/1789878789720_7822267878735642140_7822267878735642140_2b8ba36d1edddcfc1c1c86357f014f1c.jpg";
const imgRectangle2247 = `${assetPathPrefix}/59017.png`;
const imgRectangle2230 = "/1789878789707_7822267878735642140_7822267878735642140_26a47450bb6e5961cf0dcc28b177ddc8.jpg";
const imgRectangle2232 = "/1789878789720_7822267878735642140_7822267878735642140_2b8ba36d1edddcfc1c1c86357f014f1c.jpg";
const imgRectangle2245 = "/1789878789699_7822267878735642140_7822267878735642140_294ecdc0c525dd674b514b4402bcd34d.jpg";
const imgRectangle2246 = "/1789878789714_7822267878735642140_7822267878735642140_7f662cb53b21442292cb4252d1ca924e.jpg";
const imgFace51 = "/woman.svg";
const imgKLs62BxIxUVk75Ej2 = "/my_brand.svg";
const imgImage262 = "/other_brand.svg";
const imgRectangle428 = "/journey_2.svg";
const imgRectangle429 = "/journey_1.svg";
const imgRectangle430 = "/journey_3.svg";
const imgRectangle526 = "/follow_5.svg";
const imgRectangle527 = "/follow_4.svg";
const imgRectangle528 = "/follow_3.svg";
const imgRectangle529 = "/follow_1.svg";
const imgRectangle530 = "/follow_2.svg";
const imgImage257 = `${assetPathPrefix}/b8c29.png`;
const imgChatbotButton = "/chatbot2.svg";
const imgGroup1000003701 = `${assetPathPrefix}/d8253.svg`;
const imgGroup1000003637 = `${assetPathPrefix}/26a67.svg`;
const imgVector = `${assetPathPrefix}/7e70c.svg`;
const imgVector1 = `${assetPathPrefix}/fa062.svg`;
const imgVector3 = `${assetPathPrefix}/01d3a.svg`;
const imgGroup = `${assetPathPrefix}/552c1.svg`;
const imgGroup1 = `${assetPathPrefix}/cb8bd.svg`;
const imgGroup2 = "/journey_1.svg";
const imgGroup3 = "/journey_2.svg";
const imgGroup4 = "/journey_3.svg";
const imgReviewQuote = "/review.svg";
const imgTimelessSkincare = "/timeless_skincare.svg";
const imgRitualisedApproach = "/ritualised_approach.svg";
const imgBackedByTradition = "/backed_by_tradition.svg";
const imgGroup1000003638 = `${assetPathPrefix}/6c09f.svg`;
const imgGroup1000003639 = `${assetPathPrefix}/46e23.svg`;
const imgGroup1000004092 = `${assetPathPrefix}/1bcc4.svg`;
const imgItemImg = `${assetPathPrefix}/ad1e2.svg`;
const imgItemImg1 = `${assetPathPrefix}/4d421.svg`;
const imgItemImg2 = `${assetPathPrefix}/c7320.svg`;
const imgAmerican = `${assetPathPrefix}/52678.svg`;
const imgDiscover1 = `${assetPathPrefix}/e004e.svg`;
const imgImg = `${assetPathPrefix}/00274.svg`;
const imgLine12 = `${assetPathPrefix}/c457c.svg`;
const imgLine13 = `${assetPathPrefix}/78ad7.svg`;
const imgVector2 = `${assetPathPrefix}/060a2.svg`;
const imgPath600 = `${assetPathPrefix}/a16ca.svg`;
const imgLogo = "/logo 3.svg";
const imgAiAvatar = "/chatbot2.svg";
const imgStar = "/star.svg";
const imgTick = "/tick.svg";
const imgX = "/x.svg";
const cartStorageKey = 'sugar-rush-cart';

type CartProduct = {
  id: string;
  name: string;
  price: number;
  image: string;
  variant: string;
  quantity: number;
};

function addProductToCart(product: Omit<CartProduct, 'quantity'>) {
  const savedCart = window.localStorage.getItem(cartStorageKey);
  const cart: CartProduct[] = savedCart ? JSON.parse(savedCart) : [];
  const existingProduct = cart.find((item) => item.id === product.id);

  if (existingProduct) existingProduct.quantity += 1;
  else cart.push({ ...product, quantity: 1 });

  window.localStorage.setItem(cartStorageKey, JSON.stringify(cart));
  window.dispatchEvent(new CustomEvent('sugar-rush-cart-updated'));
}

function getCurrentTime() {
  return new Intl.DateTimeFormat('vi-VN', { hour: '2-digit', minute: '2-digit', hour12: false }).format(new Date());
}

function StarRating() {
  const rating = 5;

  return (
    <div className="flex items-center gap-1">
      <div style={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        {Array.from({ length: rating }, (_, index) => (
          <img key={index} alt="star" src={imgStar} style={{ width: 14, height: 14, display: 'block' }} />
        ))}
      </div>
      <span style={{ fontFamily: 'Arial, sans-serif', fontSize: 12, color: '#6f6f6f', opacity: 0.8, lineHeight: '13px' }}>10 đánh giá</span>
    </div>
  );
}

function ReviewStars() {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 2 }} aria-label="5 stars">
      {Array.from({ length: 5 }, (_, index) => (
        <img key={index} alt="star" src={imgStar} style={{ width: 14, height: 14, display: 'block' }} />
      ))}
    </div>
  );
}

function ProductCard({
  img, name, price, oldPrice, badge
}: {
  img: string; name: string; price: string; oldPrice?: string; badge?: string;
}) {
  const [isHovered, setIsHovered] = useState(false);
  const [showToast, setShowToast] = useState(false);

  function handleAddToCart() {
    addProductToCart({
      id: name,
      name,
      price: Number(price.replace(/[^0-9]/g, '')),
      image: img,
      variant: 'Dung tích tiêu chuẩn',
    });
    setShowToast(true);
    window.setTimeout(() => setShowToast(false), 2500);
  }

  return (
    <div className="flex flex-col" style={{ width: '100%' }} onMouseEnter={() => setIsHovered(true)} onMouseLeave={() => setIsHovered(false)}>
      <div className="relative" style={{ paddingBottom: '136%', overflow: 'hidden' }}>
        <img src={img} alt={name} style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover' }} />
        {badge && (
          <div style={{ position: 'absolute', top: 14, left: 14, background: '#ae7c7c', padding: '4px 8px' }}>
            <span style={{ fontFamily: 'Arial, sans-serif', fontSize: 8, color: '#fff', textTransform: 'uppercase', letterSpacing: '0.16px', lineHeight: '11px' }}>{badge}</span>
          </div>
        )}
        {
          <button type="button" onClick={handleAddToCart} style={{ position: 'absolute', left: 12, right: 12, bottom: 12, background: '#ae7c7c', color: '#fff', fontFamily: 'Arial, sans-serif', fontSize: 14, lineHeight: '1.444', border: 'none', cursor: 'pointer', padding: '10px 0', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, opacity: isHovered ? 1 : 0, transform: isHovered ? 'translateY(0)' : 'translateY(8px)', transition: 'opacity 0.2s ease, transform 0.2s ease', pointerEvents: isHovered ? 'auto' : 'none' }}>
            Thêm vào giỏ <img src={imgVector1} alt="" style={{ width: 10, height: 9 }} />
          </button>
        }
        {showToast && <div role="status" style={{ position: 'fixed', top: 72, left: '50%', zIndex: 20, transform: 'translateX(-50%)', background: '#1f5136', color: '#fff', padding: '12px 20px', fontFamily: 'Arial, sans-serif', fontSize: 14, boxShadow: '0 8px 20px rgba(0,0,0,0.2)' }}>Đã thêm vào giỏ thành công</div>}
      </div>
      <div style={{ marginTop: 16, display: 'flex', flexDirection: 'column', gap: 8 }}>
        <p style={{ fontFamily: 'Arial, sans-serif', fontSize: 12, color: '#333', textTransform: 'uppercase', letterSpacing: '1.2px', lineHeight: '15px', margin: 0 }}>{name}</p>
        <StarRating />
        <div style={{ display: 'flex', alignItems: 'baseline', gap: 8 }}>
          <span style={{ fontFamily: 'Arial, sans-serif', fontWeight: 700, fontSize: 14, color: '#ae7c7c', lineHeight: '21px' }}>{price}</span>
          {oldPrice && (
            <span style={{ fontFamily: 'Arial, sans-serif', fontWeight: 700, fontSize: 11, color: '#6f6f6f', textDecoration: 'line-through', lineHeight: '21px' }}>{oldPrice}</span>
          )}
        </div>
      </div>
    </div>
  );
}

function CheckIcon({ checked }: { checked: boolean }) {
  return (
    <img src={checked ? imgTick : imgX} alt={checked ? 'Có sẵn' : 'Không có sẵn'} style={{ width: 30, height: 30, display: 'block' }} />
  );
}

export default function App() {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chatInput, setChatInput] = useState('');
  const [chatStartedAt] = useState(getCurrentTime);
  const [chatMessages, setChatMessages] = useState<Array<{ role: 'user' | 'ai'; text: string; time: string }>>([]);
  const chatMessagesRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const messagesContainer = chatMessagesRef.current;
    if (!messagesContainer) return;

    messagesContainer.scrollTo({ top: messagesContainer.scrollHeight, behavior: 'smooth' });
  }, [chatMessages]);

  async function sendChatMessage(suggestedMessage?: string) {
    const message = (suggestedMessage ?? chatInput).trim();
    if (!message) return;

    setChatInput('');
    setChatMessages((current) => [...current, { role: 'user', text: message, time: getCurrentTime() }]);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message }),
      });
      if (!response.ok) throw new Error(`Chat request failed: ${response.status}`);
      const data = await response.json();
      setChatMessages((current) => [...current, { role: 'ai', text: data.response ?? data.reply ?? 'Không nhận được phản hồi.', time: getCurrentTime() }]);
    } catch {
      setChatMessages((current) => [...current, { role: 'ai', text: 'Không kết nối được với Python. Hãy chạy scene_1.py trước.', time: getCurrentTime() }]);
    }
  }

  return (
    <div className="home-page" style={{ fontFamily: 'Arial, sans-serif', background: '#fff', width: '100%', minHeight: '100dvh', position: 'relative' }}>

      {/* Promo Bar */}
      <div style={{ background: '#f3f1eb', height: 34, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <p style={{ fontFamily: 'Arial, sans-serif', fontSize: 11, color: '#000', letterSpacing: '0.88px', textTransform: 'uppercase', margin: 0, textAlign: 'center' }}>
          Miễn phí vận chuyển cho đơn từ 1.750.000₫ &nbsp;|&nbsp; Ưu đãi mở màn: Giảm 10% cho lần mua đầu tiên
        </p>
      </div>

      {/* Hero */}
      <div style={{ position: 'relative', height: 'min(800px, 70vw)', minHeight: 400 }}>
        <img src={imgRectangle1} alt="hero" style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover' }} />
        <div style={{ position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.2)' }} />
        {/* Nav */}
        <div className="home-nav" style={{ position: 'relative', zIndex: 2, display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '28px 120px 0' }}>
          <img src={imgLogo} alt="Brand logo" style={{ width: 180, height: 'auto', display: 'block' }} />
          <nav style={{ display: 'flex', gap: 27, alignItems: 'center' }}>
            {['Trang chủ', 'Cửa hàng', 'Về chúng tôi', 'Liên hệ'].map((item, i) => (
              <a key={item} href={item === 'Cửa hàng' ? '/shop.html' : item === 'Về chúng tôi' ? '/about-us.html' : item === 'Liên hệ' ? '/contact.html' : '/'} style={{ fontFamily: 'Arial, sans-serif', fontWeight: i === 0 ? 700 : 400, fontSize: 13, color: '#fff', textTransform: 'uppercase', letterSpacing: '1.17px', textDecoration: 'none', lineHeight: '1.361', padding: '8px 12px', border: i === 0 ? '1px solid rgba(255,255,255,0.85)' : '1px solid transparent' }}>{item}</a>
            ))}
          </nav>
          <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
            <button type="button" aria-label="Search" style={{ background: 'transparent', border: 'none', padding: 6, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                <circle cx="11" cy="11" r="6" stroke="white" strokeWidth="1.8" />
                <path d="M16 16L21 21" stroke="white" strokeWidth="1.8" strokeLinecap="round" />
              </svg>
            </button>
            <a href="/cart.html" aria-label="Cart" style={{ background: 'transparent', border: 'none', padding: 6, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                <path d="M3 4H5L6.4 14.2C6.5 15 7.2 15.6 8 15.6H17.2C17.9 15.6 18.6 15.1 18.8 14.4L20.4 8H6.1" stroke="white" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
                <circle cx="9.3" cy="18.5" r="1.5" fill="white" />
                <circle cx="17" cy="18.5" r="1.5" fill="white" />
              </svg>
            </a>
          </div>
        </div>
      </div>

      {/* Skin Care */}
      <div className="skin-section" style={{ background: '#f0ede6', display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1fr)', columnGap: 24, alignItems: 'stretch' }}>
        <div style={{ padding: '80px 0 80px 60px' }}>
          <h2 style={{ fontFamily: '"Domine:Regular", Domine, serif', fontWeight: 400, fontSize: 36, color: '#333', letterSpacing: '-0.72px', lineHeight: '45px', marginBottom: 35 }}>Chăm sóc da</h2>
          <div className="skincare-products" style={{ display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0, 1fr))', gap: 24 }}>
            <ProductCard img={imgRectangle2232} name="Nước cân bằng Sugar Rush" price="180.000₫" />
            <ProductCard img={imgRectangle2230} name="Serum phục hồi nâng cấp Sugar Rush" price="220.000₫" />
          </div>
        </div>
        <div style={{ minHeight: 480, overflow: 'hidden' }}>
          <img src={imgRectangle2252} alt="Sugar Rush skincare" style={{ width: '100%', height: '100%', minHeight: 480, objectFit: 'cover', display: 'block' }} />
        </div>
      </div>

      {/* Best Sellers */}
      <div className="best-sellers" style={{ padding: '60px 120px', background: '#fff' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: 35 }}>
          <h2 style={{ fontFamily: '"Domine:Regular", Domine, serif', fontWeight: 400, fontSize: 36, color: '#333', letterSpacing: '-0.72px', lineHeight: '45px', margin: 0 }}>Bán chạy nhất</h2>
          <button style={{ border: '1px solid #333', background: 'transparent', padding: '13px 37px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 10 }}>
            <span style={{ fontFamily: 'Arial, sans-serif', fontSize: 14, color: '#333', textTransform: 'capitalize', lineHeight: '1.444' }}>Khám phá tất cả</span>
            <img src={imgVector} alt="" style={{ width: 11, height: 9 }} />
          </button>
        </div>
        <div className="best-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 24 }}>
          <ProductCard img={imgFrame1000004406} name="Nước cân bằng Sugar Rush" price="180.000₫" />
          <ProductCard img={imgRectangle2231} name="Serum phục hồi Sugar Rush" price="220.000₫" oldPrice="260.000₫" badge="Hết hàng" />
          <ProductCard img={imgFrame1000004408} name="Kem dưỡng đậm đặc Sugar Rush" price="200.000₫" />
          <ProductCard img={imgRectangle2233} name="Sữa rửa mặt dịu nhẹ Sugar Rush" price="150.000₫" />
        </div>
      </div>

      {/* Why Choose Us */}
      <div className="why-section" style={{ background: '#f0ede6', padding: '80px 120px' }}>
        <div style={{ display: 'flex', gap: 60, flexWrap: 'wrap' }}>
          {/* Left text */}
          <div style={{ flex: '0 0 320px', display: 'flex', flexDirection: 'column', gap: 27 }}>
            <div>
              <h2 style={{ fontFamily: '"Domine:Regular", Domine, serif', fontWeight: 400, fontSize: 36, color: '#333', letterSpacing: '-0.72px', lineHeight: '45px', margin: 0 }}>
                Vì sao chọn <span style={{ fontFamily: '"Domine:Bold", Domine, serif', fontWeight: 700, color: '#ae7c7c' }}>chúng tôi</span>
              </h2>
              <p style={{ fontFamily: 'Arial, sans-serif', fontSize: 14, color: '#6f6f6f', lineHeight: '23px', letterSpacing: '0.14px', marginTop: 18 }}>
                Chọn chúng tôi vì các công thức tinh tuyển kết hợp hoàn hảo giữa các thành phần lành tính như Centella Asiatica, Probiotics và Bakuchiol, mang lại sự hài hòa và nuôi dưỡng toàn diện cho cả làn da lẫn tâm trí của bạn.
              </p>
            </div>
          </div>

          {/* Comparison table */}
          <div className="comparison-wrap" style={{ flex: '1 1 400px' }}>
            {/* Header */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', background: 'transparent', borderRadius: '17px 17px 0 0', padding: '18px 27px 0' }}>
              <span></span>
              <div style={{ display: 'flex', gap: 0 }}>
                <div style={{ background: 'transparent', width: 180, height: 150, boxSizing: 'border-box', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 12, marginTop: 0 }}>
                  <img src={imgKLs62BxIxUVk75Ej2} alt="Thương hiệu của chúng tôi" style={{ width: '100%', height: 100, objectFit: 'contain' }} />
                </div>
                <div style={{ background: 'transparent', width: 180, height: 150, boxSizing: 'border-box', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 12, marginTop: 0 }}>
                  <img src={imgImage262} alt="Thương hiệu khác" style={{ width: '100%', height: 100, objectFit: 'contain' }} />
                </div>
              </div>
            </div>
            <div style={{ border: '1px solid rgba(0,0,0,0.14)', borderRadius: 17, overflow: 'hidden' }}>
            {/* Subheader */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 180px 180px', background: '#fff', padding: '14px 27px', borderTop: '1px solid rgba(0,0,0,0.14)', borderBottom: '1px solid rgba(0,0,0,0.14)', gap: 0 }}>
              <span style={{ fontFamily: '"Domine:Regular", Domine, serif', fontSize: 17.18, color: '#333', textAlign: 'left' }}>Đặc điểm</span>
              <span style={{ fontFamily: '"Domine:Regular", Domine, serif', fontSize: 17.18, lineHeight: '1.3', color: '#333', textAlign: 'center', padding: '0 8px', borderLeft: '1px solid rgba(0,0,0,0.14)' }}>Thương hiệu của chúng tôi</span>
              <span style={{ fontFamily: '"Domine:Regular", Domine, serif', fontSize: 17.18, lineHeight: '1.3', color: '#333', textAlign: 'center', padding: '0 8px', borderLeft: '1px solid rgba(0,0,0,0.14)' }}>Thương hiệu khác</span>
            </div>
            {/* Rows */}
            {[
              { label: 'Thành phần không độc hại', mine: true, other: false },
              { label: 'Gốc rễ từ truyền thống phong phú', mine: true, other: false },
              { label: 'Tiếp cận sức khỏe toàn diện', mine: true, other: false },
            ].map((row, i) => (
              <div key={i} style={{ display: 'grid', gridTemplateColumns: '1fr 180px 180px', background: 'transparent', padding: '14px 27px', borderBottom: '1px solid rgba(0,0,0,0.14)', gap: 0, alignItems: 'center' }}>
                <span style={{ fontFamily: 'Arial, sans-serif', fontSize: 13, color: '#333', textTransform: 'uppercase', letterSpacing: 1 }}>{row.label}</span>
                <div style={{ display: 'flex', justifyContent: 'center', borderLeft: '1px solid rgba(0,0,0,0.14)' }}><CheckIcon checked={row.mine} /></div>
                <div style={{ display: 'flex', justifyContent: 'center', borderLeft: '1px solid rgba(0,0,0,0.14)' }}><CheckIcon checked={row.other} /></div>
              </div>
            ))}
            </div>
          </div>
        </div>

        {/* Icons row */}
        <div style={{ display: 'flex', gap: 80, justifyContent: 'space-between', marginTop: 60, flexWrap: 'wrap' }}>
          {[
            { img: imgTimelessSkincare, title: 'CHĂM SÓC DA VĨNH CỬU', desc: 'Khám phá các nghi thức làm đẹp lâu đời được truyền qua nhiều thế hệ. Trải nghiệm vẻ rạng rỡ và độ trẻ trung tự nhiên trong từng lần thoa.' },
            { img: imgRitualisedApproach, title: 'PHƯƠNG PHÁP NGHI THỨC', desc: 'Chúng tôi chỉ sử dụng nguyên liệu thiên nhiên tốt nhất, không chứa hóa chất khắc nghiệt, để bạn sở hữu làn da khỏe mạnh, rạng rỡ mà không phải thỏa hiệp.' },
            { img: imgBackedByTradition, title: 'DỰA TRÊN TRUYỀN THỐNG', desc: 'Dựa trên truyền thống nhưng được thiết kế cho thời đại hiện nay — chúng tôi tôn vinh trí tuệ của những người đi trước.' },
          ].map((item) => (
            <div key={item.title} style={{ display: 'flex', flex: '1 1 0', flexDirection: 'column', gap: 25, alignItems: 'center', minWidth: 240, maxWidth: 320, textAlign: 'center' }}>
              <img src={item.img} alt={item.title} style={{ width: 85, height: 85 }} />
              <div>
                <p style={{ fontFamily: 'Arial, sans-serif', fontSize: 15, color: '#333', textTransform: 'uppercase', letterSpacing: '1.5px', lineHeight: '15px', marginBottom: 13 }}>{item.title}</p>
                <p style={{ fontFamily: 'Arial, sans-serif', fontSize: 12, color: '#6f6f6f', lineHeight: '19px', margin: 0 }}>{item.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Modern Rituals / About */}
      <div style={{ background: '#E5DED1', display: 'flex', flexWrap: 'wrap', alignItems: 'stretch', minHeight: 680 }}>
        <div style={{ flex: '1 1 50%', minWidth: 280, position: 'relative', overflow: 'hidden', minHeight: 500 }}>
          <img src={imgFace51} alt="woman" style={{ width: '100%', height: 'calc(100% - 40px)', objectFit: 'contain', objectPosition: 'center bottom', position: 'absolute', top: 40, right: 0, left: 0 }} />
        </div>
        <div style={{ flex: '1 1 40%', minWidth: 280, padding: '80px 80px 80px 60px', display: 'flex', flexDirection: 'column', gap: 27, alignItems: 'flex-end', justifyContent: 'center', textAlign: 'right' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <p style={{ fontFamily: 'Arial, sans-serif', fontSize: 14, color: '#333', textTransform: 'uppercase', letterSpacing: '2.43px', lineHeight: '1.3', margin: 0 }}>Về Placeholder</p>
            <h2 style={{ fontFamily: '"Domine:Regular", Domine, serif', fontWeight: 400, fontSize: 36, color: '#333', letterSpacing: '-0.72px', lineHeight: '45px', margin: 0 }}>
              Nghi thức hiện đại cho cuộc sống tỉnh thức
            </h2>
            <p style={{ fontFamily: 'Arial, sans-serif', fontSize: 14, color: '#6f6f6f', lineHeight: '23px', letterSpacing: '0.14px', margin: 0 }}>
              Gắn bó với triết lý chăm sóc da Hàn Quốc, Placeholder biến việc chăm sóc hằng ngày thành những khoảnh khắc thư giãn và cân bằng. Chúng tôi tin vẻ đẹp phát triển từ sự đều đặn, những nghi thức đơn giản và có ý thức giúp bạn giữ sự bình ổn giữa những ngày bận rộn.
            </p>
          </div>
          <a href="/about-us.html" style={{ background: '#ae7c7c', border: 'none', padding: '13px 37px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 10, textDecoration: 'none' }}>
            <span style={{ fontFamily: 'Arial, sans-serif', fontSize: 14, color: '#fff', textTransform: 'capitalize', lineHeight: '1.444' }}>Tìm hiểu thêm</span>
            <img src="/arrow.svg" alt="" style={{ width: 11, height: 9, objectFit: 'contain' }} />
          </a>
        </div>
      </div>

      {/* Testimonials */}
      <div style={{ background: '#f9f9f7', padding: '80px 120px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 21 }}>
          {[
            { quote: '"Làn da tôi từng rất nhạy cảm và dễ kích ứng, nhưng từ khi chuyển sang các sản phẩm lành tính ở đây, da đã khỏe và dịu đi trông thấy."', author: '- Lan Anh', stars: imgGroup1000003638 },
            { quote: '"Cảm giác mỗi lần sử dụng giống như đang được thư giãn tại spa vậy. Da mềm mịn và sáng khỏe lên từng ngày."', author: '- Minh Thư', stars: imgGroup1000003638 },
            { quote: '"Thói quen chăm sóc da hằng ngày của tôi đã trở nên đơn giản nhưng hiệu quả hơn rất nhiều. Da lúc nào cũng đủ ẩm và rạng rỡ."', author: '- Khánh Linh', stars: imgGroup1000003639 },
          ].map((t) => (
            <div key={t.author} style={{ background: '#fff', padding: '34px 65px', display: 'flex', flexDirection: 'column', gap: 21, alignItems: 'center', textAlign: 'center' }}>
              <img src={imgReviewQuote} alt="" style={{ width: 21, height: 15, transform: 'rotate(180deg)' }} />
              <ReviewStars />
              <p style={{ fontFamily: 'Arial, sans-serif', fontSize: 15, color: '#333', lineHeight: '24px', margin: 0 }}>{t.quote}</p>
              <p style={{ fontFamily: 'Arial, sans-serif', fontSize: 15, color: '#ae7c7c', lineHeight: '24px', margin: 0 }}>{t.author}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Instagram */}
      <div style={{ background: '#f9f9f7', padding: '60px 0 0' }}>
        <h2 style={{ fontFamily: '"Domine:Regular", Domine, serif', fontWeight: 400, fontSize: 36, color: '#000', textAlign: 'center', letterSpacing: '-0.72px', lineHeight: '45px', marginBottom: 40 }}>
          Theo dõi chúng tôi trên <span style={{ fontFamily: '"Domine:Bold", Domine, serif', fontWeight: 700, color: '#ae7c7c' }}>Instagram</span>
        </h2>
        <div style={{ display: 'flex', gap: 0 }}>
          {[imgRectangle529, imgRectangle530, imgRectangle528, imgRectangle527, imgRectangle526].map((img, i) => (
            <div key={i} style={{ flex: 1, aspectRatio: '1', overflow: 'hidden' }}>
              <img src={img} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }} />
            </div>
          ))}
        </div>
      </div>

      {/* Journal / Blog */}
      <div style={{ background: '#f9f9f7', padding: '60px 120px 80px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: 30 }}>
          <div>
            <h2 style={{ fontFamily: '"Domine:Regular", Domine, serif', fontWeight: 400, fontSize: 36, color: '#333', letterSpacing: '-0.72px', lineHeight: '45px', margin: 0 }}>
              Từ <span style={{ fontFamily: '"Domine:Bold", Domine, serif', fontWeight: 700, color: '#ae7c7c' }}>Placeholder Journal</span>
            </h2>
            <p style={{ fontFamily: 'Arial, sans-serif', fontSize: 14, color: '#6f6f6f', lineHeight: '23px', marginTop: 9 }}>Yêu thích bởi những phụ nữ tỏa sáng tự nhiên</p>
          </div>
          <button style={{ border: '1px solid #333', background: 'transparent', padding: '13px 37px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 10 }}>
            <span style={{ fontFamily: 'Arial, sans-serif', fontSize: 14, color: '#333', textTransform: 'capitalize', lineHeight: '1.444' }}>Khám phá tất cả</span>
            <img src={imgVector} alt="" style={{ width: 11, height: 9 }} />
          </button>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 21 }}>
          {[
            { img: imgRectangle429, date: '14 tháng 11, 2024', title: 'Khoa học đằng sau liệu pháp chạm điểm: cách hoạt động, lợi ích và triển vọng', desc: 'Liệu pháp chạm điểm, một phương pháp hỗ trợ tập trung vào việc tác động lên các vị trí cụ thể trên bàn chân, tay và tai, thường gắn liền với nhiều lợi ích cho sức khỏe.' },
            { img: imgRectangle428, date: '10 tháng 11, 2024', title: 'Những đổi mới trong sức khỏe phụ nữ: cách MDIC và Heat Vibes của Bayer đang giải quyết đau và sức khỏe', desc: 'Sức khỏe phụ nữ, đặc biệt khi nói đến việc kiểm soát đau mãn tính và thúc đẩy sức khỏe, thường bị xem nhẹ trong nghiên cứu y khoa.' },
            { img: imgRectangle430, date: '10 tháng 11, 2024', title: 'Nấc thang gãy: cách phân biệt đối xử và bất bình đẳng tiếp tục cản trở phụ nữ trẻ tại nơi làm việc', desc: 'Phụ nữ trẻ ở Anh vẫn tiếp tục phải đối mặt với bất bình đẳng giới và phân biệt đối xử tại nơi làm việc, theo báo cáo mới nhất của Young Women\'s Trust.' },
          ].map((article) => (
            <div key={article.date + article.title} style={{ background: '#fff', display: 'flex', flexDirection: 'column' }}>
              <div style={{ position: 'relative' }}>
                <img src={article.img} alt={article.title} style={{ width: '100%', height: 218, objectFit: 'cover', display: 'block' }} />
                <div style={{ position: 'absolute', top: 11, left: 11, background: '#fff', padding: '7px 8px' }}>
                  <span style={{ fontFamily: 'Arial, sans-serif', fontSize: 10, color: '#333', textTransform: 'uppercase', letterSpacing: '0.2px', lineHeight: '11px' }}>{article.date}</span>
                </div>
              </div>
              <div style={{ padding: '24px 20px', display: 'flex', flexDirection: 'column', gap: 13 }}>
                <p style={{ fontFamily: 'Arial, sans-serif', fontSize: 16, color: '#333', textTransform: 'uppercase', lineHeight: '19px', margin: 0 }}>{article.title}</p>
                <p style={{ fontFamily: 'Arial, sans-serif', fontSize: 13, color: '#6f6f6f', lineHeight: '22px', margin: 0 }}>{article.desc}</p>
                <a href="#" style={{ fontFamily: 'Arial, sans-serif', fontSize: 11, color: '#333', textDecoration: 'underline', textTransform: 'uppercase', lineHeight: '1.444' }}>Tìm hiểu thêm</a>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <footer style={{ background: '#090909', padding: '60px 120px 40px', position: 'relative' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1fr)', gap: 60, marginBottom: 60 }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, minmax(0, 1fr))', gap: 32 }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 17 }}>
            <p style={{ fontFamily: 'Arial, sans-serif', fontSize: 18, color: '#fff', lineHeight: '21px', margin: 0 }}>Liên kết nhanh</p>
            <div style={{ fontFamily: 'Arial, sans-serif', fontSize: 12, color: '#fff', opacity: 0.7, lineHeight: '23px' }}>
              {['Cửa hàng', 'Về chúng tôi', 'Blog', 'Liên hệ'].map(l => <p key={l} style={{ margin: 0 }}>{l}</p>)}
            </div>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 17 }}>
            <p style={{ fontFamily: 'Arial, sans-serif', fontSize: 18, color: '#fff', lineHeight: '21px', margin: 0 }}>Mạng xã hội</p>
            <div style={{ fontFamily: 'Arial, sans-serif', fontSize: 12, color: '#fff', opacity: 0.7, lineHeight: '23px' }}>
              {[
                { label: 'Facebook', href: 'https://www.facebook.com/bangtan.official' },
                { label: 'Instagram', href: 'https://www.instagram.com/bts.bighitofficial/' },
                { label: 'YouTube', href: 'https://www.youtube.com/results?search_query=bts' },
              ].map(({ label, href }) => (
                <p key={label} style={{ margin: 0 }}>
                  <a href={href} target="_blank" rel="noreferrer" style={{ color: 'inherit', textDecoration: 'none' }}>{label}</a>
                </p>
              ))}
            </div>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 17 }}>
            <p style={{ fontFamily: 'Arial, sans-serif', fontSize: 18, color: '#fff', lineHeight: '21px', margin: 0 }}>Chính sách</p>
            <div style={{ fontFamily: 'Arial, sans-serif', fontSize: 12, color: '#fff', opacity: 0.7, lineHeight: '23px' }}>
              {['Chính sách bảo mật', 'Chính sách hoàn trả', 'Điều khoản dịch vụ', 'Chính sách vận chuyển'].map(l => <p key={l} style={{ margin: 0 }}>{l}</p>)}
            </div>
            </div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 9 }}>
            <p style={{ fontFamily: 'Arial, sans-serif', fontSize: 18, color: '#fff', lineHeight: '21px', margin: 0 }}>Nhận 10% cho đơn hàng đầu tiên</p>
            <p style={{ fontFamily: 'Arial, sans-serif', fontSize: 12, color: '#fff', opacity: 0.7, lineHeight: '20px', margin: 0 }}>Nhận lời khuyên chăm sóc da, quyền truy cập sớm vào sản phẩm mới và ưu đãi độc quyền ngay trong hộp thư của bạn.</p>
            <div style={{ marginTop: 20, display: 'flex', flexDirection: 'column', gap: 9 }}>
              <div style={{ border: '1px solid #fff', height: 48, display: 'flex', alignItems: 'center', padding: '0 16px' }}>
                <span style={{ fontFamily: 'Arial, sans-serif', fontSize: 14, color: '#fff', opacity: 0.6 }}>Địa chỉ email</span>
              </div>
              <button style={{ background: '#fff', border: 'none', height: 48, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10 }}>
                <span style={{ fontFamily: 'Arial, sans-serif', fontWeight: 700, fontSize: 14, color: '#ae7c7c' }}>Đăng ký</span>
                <img src={imgVector3} alt="" style={{ width: 11, height: 9 }} />
              </button>
            </div>
          </div>
        </div>

        {/* Footer bottom */}
        <div style={{ borderTop: '1px solid rgba(255,255,255,0.15)', paddingTop: 24, display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 16 }}>
          <img src={imgLogo} alt="Sugar Rush logo" style={{ width: 180, height: 'auto', objectFit: 'contain', display: 'block' }} />
          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            <img src="/card.svg" alt="Accepted payment cards" style={{ width: 226, height: 22, objectFit: 'contain', display: 'block' }} />
          </div>
        </div>
        <p style={{ fontFamily: 'Arial, sans-serif', fontSize: 12, color: '#fff', opacity: 0.7, lineHeight: '13px', marginTop: 16 }}>© 2025 Placeholder. Mọi quyền được bảo lưu.</p>
      </footer>

      {/* Chatbot widget */}
      <div style={{ position: 'fixed', bottom: 24, right: 24, zIndex: 50, display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 12 }}>
        <div
          style={{
            width: 'min(400px, calc(100vw - 24px))',
            height: isChatOpen ? 'min(680px, calc(100dvh - 140px))' : 0,
            opacity: isChatOpen ? 1 : 0,
            transform: isChatOpen ? 'translateY(0) scale(1)' : 'translateY(22px) scale(0.96)',
            transformOrigin: 'bottom right',
            transition: 'all 0.3s ease',
            overflow: 'hidden',
            borderRadius: 20,
            pointerEvents: isChatOpen ? 'auto' : 'none',
            boxShadow: '0 18px 40px rgba(0,0,0,0.18)',
            background: '#f5f5f5',
            border: '1px solid rgba(68, 68, 68, 0.14)',
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          <div style={{ height: 62, flexShrink: 0, background: 'linear-gradient(135deg, #3a62ff 0%, #3a62ff 100%)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 14px 0 12px', color: '#fff' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <div style={{ width: 30, height: 30, borderRadius: '50%', overflow: 'hidden', background: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <img src={imgAiAvatar} alt="AI" style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }} />
              </div>
              <div>
                <div style={{ fontSize: 16, fontWeight: 700, lineHeight: '1.2', fontFamily: 'Arial, sans-serif' }}>Sugar Rush</div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, opacity: 0.9, fontFamily: 'Arial, sans-serif' }}>
                  <span style={{ width: 7, height: 7, borderRadius: '50%', background: '#91f5a6', display: 'inline-block' }} />
                  Trực tuyến
                </div>
              </div>
            </div>
            <button type="button" onClick={() => setIsChatOpen(false)} style={{ width: 26, height: 26, borderRadius: '50%', border: 'none', background: 'rgba(255,255,255,0.18)', color: '#fff', fontSize: 18, cursor: 'pointer', lineHeight: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>−</button>
          </div>

          <div ref={chatMessagesRef} style={{ flex: '1 1 auto', minHeight: 0, background: '#f8f8f8', padding: '12px 12px 10px', display: 'flex', flexDirection: 'column', gap: 12, overflowY: 'auto' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <img src={imgAiAvatar} alt="AI" style={{ width: 26, height: 26, borderRadius: '50%', objectFit: 'cover', display: 'block' }} />
              <span style={{ fontSize: 10, color: '#666', fontFamily: 'Arial, sans-serif' }}>{chatStartedAt}</span>
            </div>

            <div style={{ maxWidth: '88%', background: '#e8e8eb', borderRadius: 14, padding: '10px 12px', fontFamily: 'Arial, sans-serif', fontSize: 13, lineHeight: '1.5', color: '#202124', alignSelf: 'flex-start' }}>
              Chào bạn! Mình là trợ lý ảo chăm sóc da của <strong>Sugar Rush</strong>. Hôm nay da của bạn đang gặp vấn đề gì (mụn, khô, thâm sạm...) hay bạn cần tìm sản phẩm nào nhỉ?
            </div>

            <div style={{ alignSelf: 'flex-end', fontSize: 10, color: '#6a6a6a', fontFamily: 'Arial, sans-serif' }}>{chatStartedAt}</div>

            {chatMessages.map((message, index) => (
              <div key={`${message.role}-${index}`} style={{ display: 'flex', flexDirection: 'column', alignItems: message.role === 'user' ? 'flex-end' : 'flex-start', gap: 3 }}>
                <div style={{ maxWidth: '84%', background: message.role === 'user' ? '#FFB5C1' : '#e8e8eb', color: '#202124', borderRadius: 14, padding: '10px 12px', fontFamily: 'Arial, sans-serif', fontSize: 13, lineHeight: '1.5' }}>
                  {message.text}
                </div>
                <span style={{ fontSize: 10, color: '#6a6a6a', fontFamily: 'Arial, sans-serif' }}>{message.time}{message.role === 'user' ? ' ✓' : ''}</span>
              </div>
            ))}
          </div>

          <div style={{ flexShrink: 0, background: '#f7f7f7', padding: '10px 12px 12px', borderTop: '1px solid rgba(0,0,0,0.06)' }}>
            <div style={{ display: 'flex', gap: 8, marginBottom: 10, flexWrap: 'wrap' }}>
              {['WappGPT là gì?', 'Bảng giá', 'Câu hỏi thường gặp'].map((item) => (
                <button key={item} type="button" onClick={() => void sendChatMessage(item)} style={{ border: '1px solid rgba(73, 78, 242, 0.2)', borderRadius: 999, background: '#fff', padding: '8px 10px', fontFamily: 'Arial, sans-serif', fontSize: 11, color: '#3a3a3a', cursor: 'pointer' }}>{item}</button>
              ))}
            </div>
            <form onSubmit={(event) => { event.preventDefault(); void sendChatMessage(); }} style={{ display: 'flex', alignItems: 'center', gap: 10, background: '#ececef', borderRadius: 16, padding: '6px 8px 6px 12px' }}>
              <input value={chatInput} onChange={(event) => setChatInput(event.target.value)} placeholder="Nhập tin nhắn của bạn..." aria-label="Chat message" style={{ flex: 1, minWidth: 0, border: 'none', outline: 'none', background: 'transparent', fontFamily: 'Arial, sans-serif', fontSize: 13, color: '#202124' }} />
              <button type="submit" aria-label="Send message" style={{ width: 30, height: 30, borderRadius: '50%', border: 'none', background: 'linear-gradient(135deg, #4b6bff 0%, #6d5ef6 100%)', color: '#fff', fontSize: 16, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>➤</button>
            </form>
          </div>
        </div>

        <button
          type="button"
          aria-label="Open chat"
          onClick={() => setIsChatOpen((prev) => !prev)}
          style={{
            border: 'none',
            background: 'transparent',
            padding: 0,
            cursor: 'pointer',
            width: 64,
            height: 79,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'transform 0.2s ease, opacity 0.2s ease',
            transform: isChatOpen ? 'scale(0.92)' : 'scale(1)',
            opacity: 1,
            pointerEvents: 'auto',
          }}
        >
          <img src={imgChatbotButton} alt="chat" style={{ width: '100%', height: '100%', objectFit: 'contain', display: 'block' }} />
        </button>
      </div>
    </div>
  );
}
