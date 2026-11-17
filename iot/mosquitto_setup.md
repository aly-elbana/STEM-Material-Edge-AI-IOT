# Your own MQTT broker on the Pi (works with NO internet - perfect for exhibitions)

```bash
sudo apt install -y mosquitto mosquitto-clients
sudo mosquitto_passwd -c /etc/mosquitto/passwd team07        # choose a password
sudo tee /etc/mosquitto/conf.d/capstone.conf > /dev/null <<'CONF'
listener 1883
allow_anonymous false
password_file /etc/mosquitto/passwd
CONF
sudo systemctl restart mosquitto
```
Test (two terminals):
```bash
mosquitto_sub -h localhost -u team07 -P <pass> -t 'stem/#' -v
mosquitto_pub -h localhost -u team07 -P <pass> -t stem/team07/test -m hello
```
Devices on the same Wi-Fi use the Pi's IP (`hostname -I`):
`export MQTT_HOST=192.168.1.50 MQTT_USER=team07 MQTT_PASS=...`

Exhibition trick: make the Pi a Wi-Fi hotspot (or use a phone hotspot) so the whole system
works without the venue's internet.
