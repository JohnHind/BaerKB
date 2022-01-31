from random import randint as rand
import adafruit_led_animation.color as C
try:
    from neopixel import NeoPixel
except ImportError:
    NeoPixel = None
try:
    from adafruit_dotstar import DotStar
except ImportError:
    DotStar = None
if NeoPixel == None and DotStar == None: raise ImportError("Neither NeoPixel nor DotStar libraries available")

class PixelMap:
    def __init__(self, strips, map, strip_period=1):
        if isinstance(strips, NeoPixel) or isinstance(strips, DotStar):
            self._pixels = [strips]
        else:
            self._pixels = [s for s in strips]
        if isinstance(self._pixels[0], NeoPixel):
            np = True
        elif not isinstance(self._pixels[0], DotStar):
            raise TypeError("Strips is not NeoPixel or DotStar")
        for s in self._pixels:
            if np and not isinstance(s, NeoPixel):
                raise TypeError("Strips must be the same type")
            if not np and not isinstance(s, DotStar):
                raise TypeError("Strips must be the same type")
        if len(self._pixels) > 1:
            self._sp = 1
            for p in self._pixels: self._sp = p.n if p.n > self._sp else self._sp
            if strip_period > self._sp: self._sp = strip_period
        else:
            self._sp = 0
        if isinstance(map[0], int):
            self._map = [[v] for v in map]
            self._rl = len(self._map)
        else:
            self._rl = len(map[0])
            self._map = []
            for r in map:
                for c in r: self._map.append(c)
        self.indexing()

    RASTER = 0
    ZIGZAG = 1
    ROWS = 2
    COLUMNS = 3

    RING = 0
    BOUNCE = 1
    RAND = 2

    def indexing(self, index_mode=None, inner_slice=None, val_mode=None, auto_update=True):
        self._im = index_mode if index_mode in (PixelMap.RASTER, PixelMap.ZIGZAG, PixelMap.ROWS, PixelMap.COLUMNS) else PixelMap.RASTER
        self._is = inner_slice if isinstance(inner_slice, slice) else None
        self._vm = val_mode if val_mode in (PixelMap.RING, PixelMap.BOUNCE, PixelMap.RAND) else PixelMap.RING
        self._au = auto_update == True

    def _indices(self, ix, mx):
        try:
            ls = []
            for i in ix:
                v = int(i)
                if v < 0: v += mx
                if v >= mx: raise IndexError("Index out of bounds in Index List")
                ls.append(v)
            return ls
        except TypeError:
            pass
        if isinstance(ix, slice):
            s, e, i = ix.indices(mx)
        else:
            s, e, i = int(ix), 0, 1
            if s < 0: s += mx
            if e <= s: e = s + 1
            if s >= mx: IndexError("Index out of bounds")
        return range(s, e, i)

    def _row_indices(self, ix):
        r = self._rl
        if ix >= (len(self._map)//r) or ix < 0: raise IndexError( "Row index out of bounds")
        s = ix * r
        e = s + r
        i = 1
        if isinstance(self._is, slice):
            xs, xe, xi = self._is.indices(r)
            s += xs
            e -= r - xe
            i = xi
        return range(s, e, i)

    def _col_indices(self, ix):
        r = self._rl
        if ix >= r or ix < 0: raise IndexError( "Column index out of bounds")
        s = ix
        e = len(self._map) - r + 1 + ix
        i = r
        if isinstance(self._is, slice):
            xs, xe, xi = self._is.indices(len(self._map) // self._rl)
            s += xs * r
            e -= len(self._map) - (xe * r)
            i *= xi
        return range(s, e, i)

    def _zigzag_index(self, ix):
        m = ix // self._rl
        return (2 * m * self._rl + self._rl - 1) - ix if m % 2 else ix

    def _val_source(self, v):
        if isinstance(v, tuple) and not isinstance(v[0], tuple): v = (v,)
        vb = self._vm if len(v) > 1 else PixelMap.RING
        ic, ix = 1, -1
        def val():
            nonlocal ix, ic
            if vb == PixelMap.RAND:
                return v[rand(0, len(v) - 1)]
            ix += ic
            if ix >= len(v):
                if vb == PixelMap.RING:
                    ix = 0
                else:
                    ic, ix = -1, len(v) - 1
            if ix < 0 and vb == PixelMap.BOUNCE:
                ix, ic = 1, 1
            return v[ix]
        return val

    def __len__(self):
        if self._im == PixelMap.ROWS:
            return len(self._map) // self._rl
        elif self._im == PixelMap.COLUMNS:
            return self._rl
        return len(self._map)

    def _setpixel(self, ix, val_source):
        c, x = val_source(), self._map[ix]
        if x is not None:
            si = x // self._sp if self._sp > 0 else 0
            self._pixels[si][x + si * self._sp] = c

    def __setitem__(self, ix, val):
        val = self._val_source(val)
        if self._im == PixelMap.ROWS:
            for i in self._indices(ix, len(self._map) // self._rl):
                for ii in self._row_indices(i):
                    self._setpixel(ii, val)
        elif self._im == PixelMap.COLUMNS:
            for i in self._indices(ix, self._rl):
                for ii in self._col_indices(i):
                    self._setpixel(ii, val)
        elif self._im == PixelMap.ZIGZAG:
            for i in self._indices(ix, len(self._map)):
                self._setpixel(self._zigzag_index(i), val)
        else: # RASTER:
            for i in self._indices(ix, len(self._map)):
                self._setpixel(i, val)
        if self._au: self.show()

    def _getpixel(self, ix):
        i = self._map[ix]
        if i is None: return C.BLACK
        si = i // self._sp if self._sp > 0 else 0
        return self._pixels[si][i + si * self._sp]

    def __getitem__(self, ix):
        rv = []
        if self._im == PixelMap.ROWS:
            for i in self._indices(ix, len(self._map) // self._rl):
                for ii in self._row_indices(i):
                    rv.append(self._getpixel(ii))
        elif self._im == PixelMap.COLUMNS:
            for i in self._indices(ix, self._rl):
                for ii in self._col_indices(i):
                    rv.append(self._getpixel(ii))
        elif self._im == PixelMap.ZIGZAG:
            for i in self._indices(ix, len(self._map)):
                rv.append(self._getpixel(self._zigzag_index(i)))
        else: # RASTER:
            for i in self._indices(ix, len(self._map)):
                rv.append(self._getpixel(i))
        if len(rv) == 1: rv = rv[0]
        return rv

    def xy(self):
        rl = self._rl
        return lambda x, y : rl * y + x

    def fill(self, color=C.BLACK):
        for p in self._pixels: p.fill(color)
        if self._au: self.show()

    def show(self):
        for p in self._pixels: p.show()

    @property
    def brightness(self):
        return self._pixels[0].brightness
    @brightness.setter
    def brightness(self, brightness):
        for p in self._pixels: p.brightness = min(max(brightness, 0.0), 1.0)

    def __repr__(self):
        return f"[PixelMap rows={len(self._map)//self._rl} cols={self._rl}]"
