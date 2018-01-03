# Google Play Music Skill

## Notes:
* At present, this is only a starter skill and can only play one track.
  I'm working with the Mycroft team on an audio service API that will let me
  "double buffer" tracks indefinitely so a station can play until the playlist
  runs out.

## Usage:
* You will need to register a Google Play Music username and password with the Mycroft
  dashboard.  Once this skill has been added, go to https://home.mycroft.ai, then to the
  "Skills" page, and enter your Google Play username and an appropriate password.  If you
  use two-factor auth on your Google account, go to https://myaccount.google.com/security
  and locate "App passwords" on that page.  Follow the instructions on the "App passwords"
  page for making a new application-specific password for your Mycroft instance.

* `play <station> on Google Play Music` : This plays a "curated station."  Often, these are
  genre stations, such as "yacht rock", but note that not all generic genres have a matching
  curated station.  For example, "jazz" doesn't seem to work yet.

