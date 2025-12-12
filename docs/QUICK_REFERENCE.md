# 🐀 Rodent AI Vision Box - Quick Reference Card

Print this card and keep it near your Raspberry Pi for quick access.

---

## Quick Commands

| Action | Command |
|--------|---------|
| **Start service** | `sudo systemctl start rodent-detection` |
| **Stop service** | `sudo systemctl stop rodent-detection` |
| **Restart service** | `sudo systemctl restart rodent-detection` |
| **Check status** | `sudo systemctl status rodent-detection` |
| **View live logs** | `sudo journalctl -u rodent-detection -f` |
| **Start camera bridge** | `docker-compose up -d` |
| **Stop camera bridge** | `docker-compose down` |
| **Test email** | `source venv/bin/activate && python utils/test_email.py` |

---

## Important URLs

| Service | URL |
|---------|-----|
| **Wyze Bridge Web UI** | `http://YOUR_PI_IP:8888` |
| **Wyze API Console** | https://developer-api-console.wyze.com/ |

---

## File Locations

| Item | Path |
|------|------|
| **Configuration** | `/home/pi/rodent-ai-vision-box/config/config.yaml` |
| **Credentials** | `/home/pi/rodent-ai-vision-box/.env` |
| **Detection Images** | `/home/pi/rodent-ai-vision-box/data/images/` |
| **Logs** | `/home/pi/rodent-ai-vision-box/data/logs/` |
| **Database** | `/home/pi/rodent-ai-vision-box/data/detections.db` |

---

## Troubleshooting Checklist

- [ ] Is the Pi powered on and connected to WiFi?
- [ ] Is Docker running? (`docker ps`)
- [ ] Is Wyze Bridge showing your camera? (check :8888)
- [ ] Are Wyze credentials correct in `.env`?
- [ ] Is the detection service running? (`systemctl status`)

---

## Support Contact

Developer: Zakaria Masood
Email: mzakariamasood@gmail.com

---

