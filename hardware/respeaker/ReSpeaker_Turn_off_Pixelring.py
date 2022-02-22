# Turn off the blue voice-activation lights so GLaDOS does not look like a disco
# Run at startup with root crontab

import time
from pixel_ring import pixel_ring
pixel_ring.off()