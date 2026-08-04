/* @agent-sprite: Агент Омега — 2D піксельний персонаж.
 * Ядро (Ω, душа) світиться й пульсує. Малюється на canvas без зовнішніх залежностей.
 * Чистий ігровий контент. */
(function () {
  // Палітра (індекс → колір). 0 = прозорий.
  const PAL = {
    0: null,
    1: '#14142a', // тіло-тінь (bg3)
    2: '#23233f', // тіло-контур (border)
    3: '#7c6af7', // мантія (accent violet)
    4: '#4cc9f0', // акцент-край (cyan)
    5: '#06ffa5', // очі (green)
    9: 'CORE'     // ядро Ω — пульсує (accent2 pink → white)
  };

  // 20x20 спрайт: капюшонна фігура з Ω-ядром у грудях.
  const S = [
    "00000003333000000000",
    "00000333333330000000",
    "00003322222233000000",
    "00033222222223300000",
    "00032255225522300000",
    "00032255225522300000",
    "00032222222222300000",
    "00033222222223300000",
    "00003322222233000000",
    "00000332222330000000",
    "00003333333333000000",
    "00033344444443300000",
    "00332239999322330000",
    "03322399999932233000",
    "03222399999932223000",
    "03222339999332223000",
    "00322233333322230000",
    "00033222222222330000",
    "00000333333333000000",
    "00000033000330000000"
  ];

  function draw(canvas) {
    const ctx = canvas.getContext('2d');
    const px = Math.floor(canvas.width / S[0].length);
    let t = 0;

    function frame() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      // пульсація ядра: 0..1
      const pulse = 0.5 + 0.5 * Math.sin(t / 22);
      const core = mix('#f72585', '#ffffff', pulse * 0.7);
      for (let y = 0; y < S.length; y++) {
        for (let x = 0; x < S[y].length; x++) {
          const c = S[y][x];
          let col = PAL[c];
          if (col === 'CORE') {
            col = core;
            // легке світіння навколо ядра
            ctx.shadowColor = '#f72585';
            ctx.shadowBlur = 6 + 8 * pulse;
          } else {
            ctx.shadowBlur = 0;
          }
          if (col) {
            ctx.fillStyle = col;
            ctx.fillRect(x * px, y * px, px, px);
          }
        }
      }
      ctx.shadowBlur = 0;
      t++;
      canvas._raf = requestAnimationFrame(frame);
    }
    frame();
  }

  function mix(a, b, k) {
    const pa = parseInt(a.slice(1), 16), pb = parseInt(b.slice(1), 16);
    const ar = pa >> 16, ag = (pa >> 8) & 255, ab = pa & 255;
    const br = pb >> 16, bg = (pb >> 8) & 255, bb = pb & 255;
    const r = Math.round(ar + (br - ar) * k);
    const g = Math.round(ag + (bg - ag) * k);
    const bl = Math.round(ab + (bb - ab) * k);
    return 'rgb(' + r + ',' + g + ',' + bl + ')';
  }

  window.OmegaSprite = { draw };
})();
