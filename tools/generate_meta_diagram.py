import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch

fig, ax = plt.subplots(1, 1, figsize=(20, 13))
ax.set_xlim(0, 20)
ax.set_ylim(0, 13)
ax.axis('off')
fig.patch.set_facecolor('#F0F3F4')

# Colors
C_SAFE_BM     = '#1C2833'
C_EXEC_BM     = '#1A5276'
C_EXEC_BM2    = '#145A32'
C_EXEC_BM3    = '#6E2F6E'
C_SAFETY_PRF  = '#7D6608'
C_ADS_PRF     = '#1E8449'
C_AD_ACCOUNT  = '#922B21'
C_PIXEL       = '#4A235A'
C_WARNING     = '#784212'
WHITE         = 'white'
DARK          = '#1C2833'

def box(ax, x, y, w, h, color, lines, fontsize=7, alpha=1.0):
    b = FancyBboxPatch((x - w/2, y - h/2), w, h,
                       boxstyle="round,pad=0.06",
                       facecolor=color, edgecolor=WHITE,
                       linewidth=1.8, alpha=alpha, zorder=3)
    ax.add_patch(b)
    n = len(lines)
    spacing = 0.22
    total = (n - 1) * spacing
    for i, (txt, bold, size) in enumerate(lines):
        offset = total/2 - i * spacing
        ax.text(x, y + offset, txt, ha='center', va='center',
                fontsize=size or fontsize,
                fontweight='bold' if bold else 'normal',
                color=WHITE, zorder=4)

def arrow(ax, x1, y1, x2, y2, dashed=False, color='#555'):
    style = 'dashed' if dashed else 'solid'
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=color,
                                lw=1.4, linestyle=style))

def label(ax, x, y, txt, size=7, color=DARK, bold=False):
    ax.text(x, y, txt, ha='center', va='center', fontsize=size,
            fontweight='bold' if bold else 'normal', color=color)

# ── TITLE ──────────────────────────────────────────────
ax.text(10, 12.6, 'Meta Advertising Infrastructure', ha='center',
        fontsize=16, fontweight='bold', color=DARK)
ax.text(10, 12.25, 'Current Setup — March 2026', ha='center',
        fontsize=9, color='#666')

# ── SAFE BM (top centre) ───────────────────────────────
box(ax, 10, 11.2, 5.5, 1.0, C_SAFE_BM, [
    ('SAFE BM  —  PIXEL SAFEHOUSE', True, 8.5),
    ('Stores all pixels. NEVER runs ads.', False, 7),
])

# Safety profiles under Safe BM
box(ax, 7.5, 9.6, 3.2, 0.75, C_SAFETY_PRF, [
    ('SAFETY PROFILE 1', True, 7.5),
    ('Scott', False, 7),
])
box(ax, 12.5, 9.6, 3.2, 0.75, C_SAFETY_PRF, [
    ('SAFETY PROFILE 2', True, 7.5),
    ('Safe BM Profile', False, 7),
    ('kornsycierogix@hotmail.com', False, 6),
])

arrow(ax, 8.8, 10.7, 8.3, 9.98)
arrow(ax, 11.2, 10.7, 11.7, 9.98)

# Pixel note
ax.text(10, 9.55, '[ Pixels created here, then shared to each Execution BM ]',
        ha='center', fontsize=7.5, color=C_PIXEL, style='italic')

# ── EXECUTION BM #1 ────────────────────────────────────
box(ax, 3.5, 8.1, 5.2, 0.85, C_EXEC_BM, [
    ('EXECUTION BM #1', True, 8),
    ('ClientInsure  |  LeapQuote  |  LifeFinder', False, 7),
])

# Ad accounts
box(ax, 1.6, 6.6, 2.2, 0.7, C_AD_ACCOUNT, [
    ('AD ACCOUNT', True, 7),
    ('ClientInsure', False, 6.5),
])
box(ax, 3.5, 6.6, 2.2, 0.7, C_AD_ACCOUNT, [
    ('AD ACCOUNT', True, 7),
    ('LeapQuote', False, 6.5),
])
box(ax, 5.4, 6.6, 2.2, 0.7, C_AD_ACCOUNT, [
    ('AD ACCOUNT', True, 7),
    ('LifeFinder', False, 6.5),
])

arrow(ax, 2.5, 7.68, 2.0, 6.95)
arrow(ax, 3.5, 7.68, 3.5, 6.95)
arrow(ax, 4.5, 7.68, 5.0, 6.95)

# Profiles BM1
box(ax, 1.6, 5.3, 2.6, 0.75, C_ADS_PRF, [
    ('Kayla Peterson', True, 7),
    ('gahntokitafhu@hotmail.com', False, 5.8),
])
box(ax, 3.5, 5.3, 2.6, 0.75, C_ADS_PRF, [
    ('Media Buying Profile #1', True, 7),
    ('hairepdubily5vfl@hotmail.com', False, 5.8),
])
box(ax, 5.4, 5.3, 2.6, 0.75, C_ADS_PRF, [
    ('Media Buying Profile #2', True, 7),
    ('hopkadgalde5l4f@hotmail.com', False, 5.8),
])

arrow(ax, 1.6, 6.25, 1.6, 5.68)
arrow(ax, 3.5, 6.25, 3.5, 5.68)
arrow(ax, 5.4, 6.25, 5.4, 5.68)

# ── EXECUTION BM #2 ────────────────────────────────────
box(ax, 10, 8.1, 5.2, 0.85, C_EXEC_BM2, [
    ('EXECUTION BM #2', True, 8),
    ('No Ad Accounts Yet', False, 7),
])

box(ax, 8.3, 6.6, 2.6, 0.7, C_AD_ACCOUNT, [
    ('NO AD ACCOUNTS', True, 7),
    ('Pending setup', False, 6.5),
], alpha=0.4)

box(ax, 8.3, 5.3, 2.6, 0.75, C_ADS_PRF, [
    ('Kayla Peterson', True, 7),
    ('gahntokitafhu@hotmail.com', False, 5.8),
])
box(ax, 10.0, 5.3, 2.6, 0.75, C_ADS_PRF, [
    ('Media Buying Profile #1', True, 7),
    ('hairepdubily5vfl@hotmail.com', False, 5.8),
])
box(ax, 11.7, 5.3, 2.6, 0.75, C_ADS_PRF, [
    ('Media Buying Profile #2', True, 7),
    ('hopkadgalde5l4f@hotmail.com', False, 5.8),
])

arrow(ax, 9.2, 7.68, 8.7, 6.95)
arrow(ax, 8.3, 6.25, 8.3, 5.68)
arrow(ax, 10.0, 6.25, 10.0, 5.68)
arrow(ax, 11.7, 6.25, 11.7, 5.68)

# ── EXECUTION BM #3 ────────────────────────────────────
box(ax, 16.5, 8.1, 5.2, 0.85, C_EXEC_BM3, [
    ('EXECUTION BM #3', True, 8),
    ('Nalu  |  Brand Unknown', False, 7),
])

box(ax, 15.2, 6.6, 2.6, 0.7, C_AD_ACCOUNT, [
    ('AD ACCOUNT', True, 7),
    ('Nalu', False, 6.5),
])
box(ax, 17.8, 6.6, 2.6, 0.7, C_AD_ACCOUNT, [
    ('AD ACCOUNT', True, 7),
    ('Brand Unknown', False, 6.5),
])

arrow(ax, 15.7, 7.68, 15.4, 6.95)
arrow(ax, 17.3, 7.68, 17.6, 6.95)

box(ax, 14.5, 5.3, 2.6, 0.75, C_ADS_PRF, [
    ('Kayla Peterson', True, 7),
    ('gahntokitafhu@hotmail.com', False, 5.8),
])
box(ax, 16.5, 5.3, 2.6, 0.75, C_ADS_PRF, [
    ('Media Buying Profile #1', True, 7),
    ('hairepdubily5vfl@hotmail.com', False, 5.8),
])
box(ax, 18.5, 5.3, 2.6, 0.75, C_ADS_PRF, [
    ('Media Buying Profile #2', True, 7),
    ('hopkadgalde5l4f@hotmail.com', False, 5.8),
])

arrow(ax, 15.2, 6.25, 14.8, 5.68)
arrow(ax, 16.5, 6.25, 16.5, 5.68)
arrow(ax, 17.8, 6.25, 18.2, 5.68)

# ── PIXEL SHARE ARROWS (dashed from Safe BM) ──────────
arrow(ax, 7.75, 10.7, 3.5, 8.53, dashed=True, color=C_PIXEL)
arrow(ax, 10.0, 10.7, 10.0, 8.53, dashed=True, color=C_PIXEL)
arrow(ax, 12.25, 10.7, 16.5, 8.53, dashed=True, color=C_PIXEL)

ax.text(5.5, 9.85, 'Pixel shared', fontsize=6.5, color=C_PIXEL, style='italic', rotation=20)
ax.text(10.1, 9.6, 'Pixel shared', fontsize=6.5, color=C_PIXEL, style='italic')
ax.text(14.2, 9.85, 'Pixel shared', fontsize=6.5, color=C_PIXEL, style='italic', rotation=-20)

# ── WARNING BOX ────────────────────────────────────────
warn = FancyBboxPatch((0.3, 3.4), 19.4, 1.5,
                      boxstyle="round,pad=0.1",
                      facecolor='#FEF9E7', edgecolor='#F39C12',
                      linewidth=2, zorder=2)
ax.add_patch(warn)
ax.text(10, 4.75, 'RISK FLAG', ha='center', fontsize=8.5,
        fontweight='bold', color='#E67E22')
warnings = [
    'The same 3 profiles (Kayla, MB#1, MB#2) are admins across ALL 3 execution BMs.',
    'If any one of these profiles gets flagged, Meta can take down all 3 BMs simultaneously.',
    'Recommended fix: dedicate separate profiles per execution BM as soon as clean accounts are sourced.',
]
for i, w in enumerate(warnings):
    ax.text(10, 4.42 - i * 0.3, w, ha='center', fontsize=7.2, color='#784212')

# ── LEGEND ─────────────────────────────────────────────
items = [
    (C_SAFE_BM,    'Safehouse / Pixel BM'),
    (C_EXEC_BM,    'Execution BM #1'),
    (C_EXEC_BM2,   'Execution BM #2'),
    (C_EXEC_BM3,   'Execution BM #3'),
    (C_SAFETY_PRF, 'Safety Profile (no ads)'),
    (C_ADS_PRF,    'Advertising Profile'),
    (C_AD_ACCOUNT, 'Ad Account'),
]
ax.text(1.0, 3.1, 'Legend', fontsize=8, fontweight='bold', color=DARK)
for i, (color, lbl) in enumerate(items):
    lx = 0.5 + (i % 4) * 4.8
    ly = 2.65 - (i // 4) * 0.45
    b = FancyBboxPatch((lx, ly - 0.14), 0.32, 0.28,
                       boxstyle="round,pad=0.03",
                       facecolor=color, edgecolor=WHITE, linewidth=1, zorder=3)
    ax.add_patch(b)
    ax.text(lx + 0.45, ly, lbl, ha='left', va='center', fontsize=7, color=DARK)

plt.tight_layout(pad=0.5)
out_pdf = 'output/meta-infrastructure-diagram.pdf'
out_png = 'output/meta-infrastructure-diagram.png'
plt.savefig(out_pdf, format='pdf', bbox_inches='tight', facecolor='#F0F3F4')
plt.savefig(out_png, format='png', bbox_inches='tight', dpi=150, facecolor='#F0F3F4')
print(f'Saved: {out_pdf}')
print(f'Saved: {out_png}')
