#!/bin/bash
tail -f logs/sys.log | grep -n --color=auto $(date +%F)
