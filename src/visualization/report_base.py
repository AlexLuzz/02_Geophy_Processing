from abc import ABC, abstractmethod
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from pathlib import Path
from contextlib import contextmanager

class ReportBase(ABC):
    def __init__(self, filepath: str | Path):
        self.filepath = Path(filepath)
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        self.pdf = None

    def __enter__(self):
        self.pdf = PdfPages(self.filepath)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.pdf:
            self.pdf.close()

        if exc_type:
            print(f"\n❌ CRASH DETECTED: {exc_val}")
        else:
            print(f"\n✓ Report saved: {self.filepath}")

    @contextmanager
    def page(
        self,
        rows=1,
        cols=1,
        height_ratios=None,
        width_ratios=None,
        landscape=False,
    ):
        """Yields a gridspec page and automatically saves/closes it upon exit."""

        # A4 dimensions in inches
        page_width, page_height = (11.69, 8.27) if landscape else (8.27, 11.69)

        fig = plt.figure(figsize=(page_width, page_height), constrained_layout=True)

        gs = fig.add_gridspec(
            nrows=rows,
            ncols=cols,
            height_ratios=height_ratios,
            width_ratios=width_ratios,
            hspace=0.1,
            wspace=0.05,
        )

        try:
            yield fig, gs
        finally:
            if self.pdf:
                self.pdf.savefig(fig, bbox_inches='tight')
            plt.close(fig)

    @abstractmethod
    def build(self):
        pass
