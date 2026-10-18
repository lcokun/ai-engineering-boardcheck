# Week 1 Observation Sheet: Spotify Home Feed Recommendations

Group Part A deliverable. Observations are stated as facts; inferences are labelled "Hypothesis". Screenshots are stored in `docs/evidence/`, with personal details blurred.

| Field | Entry |
|---|---|
| System name | Spotify Home Feed Recommendation System |
| Group members | AMIL HAKIM BIN ANUAR (A24AI0014)<br>AHMAD IRFAN JOHAN BIN MAZLAN (A24AI0008)<br>AIMAN WAFI BIN BADARUL MUKRIM (A24AI0010)<br>MUHAMMAD FARIS HAZIQ BIN MOHD FARDZLEISHAM (A24AI0054)<br />MUHAMMAD AMIR REDZUAN BIN SUPRI (A24AI0112) |
| Date of observation | 18 October 2026 |
| Accounts used | Main: Amil's account (Premium, web player). Control: logged-out web player in an incognito window (no account). A Free-tier account was not tested. |

## 1. What problem does this system solve? Who benefits?

Problem: Spotify's catalogue is too large to be browsed manually, and most listeners do not know in advance which new tracks or podcasts they would like. What is shown on Home is predicted from past listening, so no search is required from the user.

Beneficiaries: music and podcasts are discovered by listeners without searching; artists and podcasters are reached by people who would never look them up by name; more listening time is gained by Spotify, through which subscribers are retained and ad revenue is earned on the Free tier.

These goals are not always aligned. Under Spotify's Discovery Mode, a reduced royalty rate is accepted by artists in exchange for extra algorithmic exposure in Radio, Autoplay and some Mixes, so part of what is heard by a listener is shaped by a commercial arrangement as well as by their taste. This is revisited in Section 6.

## 2. Which AI stack layer is most visible to users?

Layer: Application (circle one: ~~Model~~ / ~~Infrastructure~~)

Explanation: Only Home is seen by users. This consists of the shelves (Recommended Stations, Recommended for today, Recents, Your top mixes), the All / Music / Podcasts filter chips, and the right-click menus. The taste-profile model, embeddings, ranking and serving infrastructure are kept hidden.

The model layer is still exposed more than in a chatbot. Every shelf, its position and its contents are decided by the model, so the screen seen by a user is the model's output, even though the way it was produced cannot be inspected.

## 3. Quality dimensions (with measurement method)

Each dimension was measured on the top 10 items of Home (first shelves, left to right) on the main account, and on the control where applicable.

| # | Dimension | Measurement method |
|---|---|---|
| 1 | Relevance | Each of the top 10 items was rated by the account owner as relevant or not relevant to their taste. Precision@10 = relevant ÷ 10. |
| 2 | Responsiveness | 5 tracks by 4 artists (about 1 minute each) from a genre absent from the owner's recent listening were played, and Home was then refreshed. Related items were counted, excluding "Recents" and "Jump back in", since history rather than recommendations is shown there. |
| 3 | Personalisation | The main account's top 10 was compared with the control's: the number of items appearing in both was counted, and shelf types found only on the personalised feed were noted. |
| 4 | Transparency | Each shelf title was checked for whether a specific reason ("More like *Artist X*") or a generic one ("Recommended for today") is given. Menu options (track and station) that explain a recommendation were also counted, along with radio-queue tracks carrying a promoted or sponsored label. |
| 5 | Fairness (artist exposure) | The top 10 was classified by whether the artist was already known to the owner, and by local (Malaysian or regional) versus international. |

Results:

| Dimension | Main account | Control |
|---|---|---|
| Relevance (precision@10) | 10/10 = 1.0 (every item would be played by the owner) | n/a |
| Responsiveness (new-genre items after refresh, excluding history shelves) | 0 of 18 Home items, and 0 of 15 under Recommended for today → Show all, related to fantasy / tavern / game music (after 5 tracks by 4 artists) | n/a |
| Overlap with control (items in both top 10s) | 0 | 0 |
| Specific explanations | 0 of 2 recommendation shelves (generic subtitles are used on both); 0 of 21 menu options (track and station) explain a recommendation; 0 of 49 radio-queue tracks labelled | 0 (all shelves are popularity-based: Trending, Popular) |
| Known / new artists | Items: 4 known, 4 new (of 8 visible). Artists: 6 of 16 named artists known (xaptiox, AKIBA, lovekurousa, TOKYOPILL, aak3, usedcvnt), 10 new | n/a (no owner) |
| Local / international in top 10 | Not determinable: most are anonymous internet producers with no listed country; no identifiably Malaysian artist | Mostly global pop and K-pop; at least 1 Indonesian track in Trending songs |

## 4. What did the system do WELL? (specific example + evidence)

Artists unknown to the owner were recommended, and they were still judged relevant. All 10 top Home items were rated relevant by the owner (precision@10 = 1.0), and 4 of the 8 visible items were by artists the owner had never heard of: Sugure Joka Radio, 2 star, frxgxd and snafu. Of the 16 artists named on those items, 10 were new to the owner.

On the Recommended Stations shelf, familiar artists are paired with unfamiliar ones. In *xaptiox Radio*, for example, known artists (AKIBA, lovekurousa) are listed next to an unknown one (GnB Chili). Hypothesis: the pairing is deliberate, so that an unfamiliar artist is perceived as a safe try.

When the shelf was scrolled, 4 more radios were revealed (Sewerslvt, usedcvnt, kittyslvt, 68+1), all built around artists known to the owner. This makes 7 of 8 station seeds known, which is consistent with the shelf's own subtitle ("based on your favorite songs and artists"). The one unknown seed, Sugure Joka, is listed among the artists of *68+1 Radio*, which is known to the owner. Hypothesis: new seeds are selected for their closeness to known favourites. Evidence: `evidence/e1_home_before.png`, `evidence/e1b_stations_scrolled.png`.

Every new artist was drawn from the same niche (breakcore, hyperpop, underground electronic), so discovery was confined to the owner's existing taste. This is developed further in Risk 2.

## 5. What did the system do POORLY? (specific example + evidence)

Home was not adapted within the session. Five fantasy / tavern / game-music tracks by four artists (Derek Fiechter, Malukah, Alina Gingertail, Borislav Slavov) were played. This genre is absent from the owner's recent listening; one related track is kept in an old playlist that is no longer used. After refreshing, nothing from the new genre was shown on the recommendation shelves, although all five plays were confirmed as logged in Recents.

The shelves can be changed: the Stations shelf was reshuffled, and AKIBA and Aicry radios were swapped in. Every change was kept inside the existing niche, and the new genre was reflected in 0 of 18 recommendation items. For a user whose taste is shifting, or who wants to explore, no sign is given that the new listening was noticed. Evidence: `evidence/e2_home_after.png`, `evidence/e2_recents_logged.png`.

The profile is also protected by the same behaviour from one-off plays, such as a sibling using the account or a single curious search. From one session, it cannot be determined whether new signals are damped deliberately or Home is simply recomputed on a schedule. This could be settled by checking the next Discover Weekly refresh, which could not be done within the lab window.

## 6. Responsible AI risks: who is harmed and how?

**Risk 1: Undisclosed commercial influence on recommendations (Transparency, Fairness)**
Tracks whose artists accepted lower royalties are boosted by Discovery Mode, and no indication that a track was boosted was found anywhere in the interface. Taste-based picks cannot be distinguished from paid-for ones by listeners, and artists who cannot afford the royalty cut are placed at a disadvantage. Evidence: no promoted, sponsored or other label was found on any of the 49 tracks in the *xaptiox Radio* queue (Radio is a Discovery Mode context), and no "why" option is offered in either the track menu or the station menu (`e5_queue_1.png` to `e5_queue_3.png`, `e5_track_menu.png`). Whether any specific track was boosted could not be confirmed, and no means of checking is available to a listener either.

**Risk 2: Taste lock-in / filter bubble (Fairness, user autonomy)**
Once a profile is established, recommendations are pushed deeper into the same niche and new signals are ignored, so a user's exposure is narrowed over time. Listeners whose taste is changing or who want to explore are harmed, as are artists outside the user's niche, who are rarely surfaced. Evidence: 0 of 18 matching recommendation items were produced by 5 plays from 4 fantasy / game-music artists, while the shelves were reshuffled only within the existing niche (`e2_home_after.png`, `e2_recents_logged.png`). The same pattern is shown from the other side in Section 4, where all 10 newly discovered artists were drawn from the owner's niche. Counterpoint: the profile is protected by the same damping from one-off plays on a shared device, and "Exclude from your taste profile" is offered by Spotify as a manual fix.

**Risk 3: Popularity bias for new and logged-out users (Fairness)**
With no history, every item on Home is a major global or K-pop act. The established account is dominated by small underground artists, so popularity bias is mainly experienced by cold-start users. Small and local artists are kept invisible to new users while their taste is being formed, and new listeners are steered toward what is already popular. Both regimes are shown on the owner's own account: music is personalised, but the Podcasts tab is based on popularity and region, because no podcast history exists. Evidence: `e3_compare.png` (zero overlap; logged-out feed entirely popularity-based), `e3_podcasts.png`.

**Risk 4: Explicit content on shared accounts (Safety)**
Explicit content was found enabled on the main account, and it was never knowingly turned on by the owner. When it is enabled, explicit music and podcasts are played freely, and the only safeguard is a single toggle in Settings (`e4_explicit_setting.png`). Minors listening on a parent's or sibling's account are exposed. The risk is increased by three observations:
- The E tag is not shown on recommendation cards. An album that appeared clean in the grid was found to contain an explicit track once opened (`e4_album_explicit.png`).
- Explicit-tagged podcast episodes, some with adult-themed titles, were recommended on the Podcasts chip (`e4_podcasts_explicit.png`).
- Only language is covered by the E tag. Radio tracks with titles referring to self-harm and despair carried no tag or advisory (`e5_queue_1.png`), so heavy themes would not be caught even by a correctly set filter.

**Risk 5 (Hypothesis): Recommendations based on inferred sensitive attributes (Privacy, Fairness)**
Quran recitation and shows in Malay, Mandarin and other regional languages were included in the podcast feed, apparently based on location rather than listening history. If religion, ethnicity or language is inferred by Spotify from a user's location, sensitive attributes that were never shared by the user are being acted on, and users may be stereotyped or exposed by their feed. Evidence: the content is shown in `e3_podcasts.png`. The inference itself remains a hypothesis, because the same feed would be produced by regional popularity.

## 7. If you could fix ONE thing, what and why?

A "Why am I hearing this?" option should be added to every recommended track and station, with Discovery Mode boosts disclosed in it.

Changes to the profile are already allowed: "Exclude from your taste profile" is provided in both the track and station menus. However, the reason behind any recommendation still cannot be seen. None of the 21 menu options checked explains a recommendation, and none of the 49 radio tracks is labelled, although Radio is a Discovery Mode context. If the signals used were named in a per-item panel (for example "because *xaptiox* and *AKIBA* are played" or "boosted via Discovery Mode"), Risk 1 would be addressed directly, and users would be shown when their feed is narrowing (Risk 2). The Exclude control would also be easier to use well, because it would be clear what was being removed.

## Appendix A: Observation log (the 5 lab tasks)

| Task | Procedure | Observation (fact) | Hypothesis (inference) | Evidence file |
|---|---|---|---|---|
| 1. What's on Home now? Can we explain it? | Home was screenshotted; each of the top 10 items was explained by the owner | Two recommendation shelves were present: Recommended Stations ("Non-stop music based on your favorite songs and artists": Sugure Joka, xaptiox, TOKYOPILL, aak3 radios) and Recommended for today ("Inspired by your recent activity"). Both are dominated by niche breakcore / hyperpop / underground artists. Listening history is shown on the other shelves (quick-access grid, Recents). A blank green tile was displayed instead of cover art for one item. All 10 were rated relevant by the owner; 4 of the 8 visible items were by artists new to the owner. | Stations are seeded from the most-played artists; recent days of listening are weighted in Recommended for today. | `e1_home_before.png` |
| 2. Search something unusual: does the feed change? | 5 fantasy / tavern / game-music tracks by 4 artists (Derek Fiechter *The Captain's Inn*, *Black Wolf's Inn*; Malukah *The Dragonborn Comes*; Alina Gingertail *Sera was never*; Borislav Slavov *I Want to Live*) were searched and played for about 1 minute each, with no likes or saves; Home was then refreshed | All 5 plays were logged (Recents: "Today: 5 songs played"). No fantasy / tavern / game-music items were shown on the recommendation shelves: all 8 Recommended Stations and all 10 visible Recommended for today items remained breakcore / hyperpop / underground electronic. The Stations shelf was reshuffled: TOKYOPILL and Sewerslvt radios (now listed under Recents) were dropped and replaced by AKIBA and Aicry radios from the same niche. | Recommendation shelves are recomputed in batches rather than in real time, or 5 short plays are outweighed by a strong established profile. Not tested: whether the plays are picked up later by Discover Weekly (refreshed on Mondays), which would distinguish batch updating from deliberate damping. | `e2_home_after.png`, `e2_recents_logged.png` |
| 3. Differences across content types / users | The Music and Podcasts chips were compared; the main account was compared with the control | No overlap was found between personalised Home and logged-out Home. Only popularity shelves are shown on logged-out Home (Trending songs, Popular artists, Popular albums, Popular radio): Billie Eilish, Ariana Grande, The Weeknd, Lady Gaga, JENNIE, ROSÉ, SEVENTEEN, SZA, Maroon 5. Indonesian-language content is included in its Trending songs, and users are prompted to follow podcasts. On the main account, music recommendations are drawn from one deep niche, while podcast recommendations are broad, regional and multilingual: Malaysian English (The Lek Lu Podcast, Mr Money TV, The Game Of Impossible), Malay (Financial Faiz), Malaysian Mandarin (LetsTalk 马来西亚), Indonesian (sini gue ceritain), Vietnamese (HSK3 Chinese lessons), Arabic (Quran recitation), plus US and European shows. Most podcast cards are labelled Video, and generic shelf labels are used ("Episodes you might like", "Episodes to try", "Videos you might like"). Effectively no podcast history exists on the owner's account (one listen, years ago). | Without history, recommendations fall back to popularity (cold start). Since regional content appears with no account, location (probably IP-based) is used as a signal even without login. Free vs Premium was not tested. With no podcast history, podcast recommendations fall back to region and popularity inside an otherwise heavily personalised account; music taste is not carried over (no music, anime or game shows were recommended). Video podcasts appear to be promoted by Spotify, given the number of Video cards. | `e3_compare.png`, `e3_podcasts.png` |
| 4. Inappropriate / harmful content? | Settings → Explicit content was checked; Recommended for today → Show all (15 items) was opened | Allow explicit content is enabled; it was never knowingly changed by the owner. No E badge is shown on any of the 15 Recommended for today music items in grid view, but when one of them was opened (68+1, *echoes of the past*), 1 of its 12 tracks was found tagged E (*heartbroken*), so explicit labels are hidden on grid cards. On the Podcasts chip, the E tag is carried by several recommended episodes (Yum Cha Sessions, ChainsFR, AL Kate & All Their Mates, two 无码聊天室 episodes), one with a sensational adult-themed title about a drunken nightclub incident. Nothing illegal was observed. In the *xaptiox Radio* queue, self-harm and emotional distress are referred to in several track titles (e.g. *self-harm was not necessary*, *invalid emotions*, *Despair Code*), with no E tag or advisory, because only language is covered by the tag. A warning is displayed on the settings page: "It may take some time for your experience to update." | On a shared or family account, explicit music and podcasts are played unless the setting is switched off by an adult who knows about it. The settings warning indicates that preference changes are applied with a delay, which is consistent with the lag observed in Task 2. | `e4_explicit_setting.png`, `e4_recommended_all.png`, `e4_album_explicit.png`, `e4_podcasts_explicit.png` |
| 5. Why is it recommended? | Shelf titles were read; the menu was opened on a recommended track and on a station card; *xaptiox Radio* was played and its whole queue was scrolled | Why anything was recommended is not explained by any option. Track menu (11 options): Add to playlist, Save to Liked Songs, Add to queue, Hide in this album, Exclude from your taste profile, Start a Jam, Sleep timer, Go to song radio, Go to artist, View credits, Share. No "Not interested" option is provided. Exclude from your taste profile is included in the station menu (10 options), but Report is greyed out. Queue: 49 tracks, none carrying a promoted, sponsored or any other label; a music video was inserted into the audio station as one item. | The profile can be changed by users (Exclude), but the reasons behind a recommendation cannot be seen. Because Discovery Mode boosts are unlabelled, whether any of the 49 tracks were boosted cannot be determined. With Report disabled on algorithmic stations, no channel is provided for flagging them. | `e5_track_menu.png`, `e5_station_menu.png`, `e5_queue_1.png` to `e5_queue_3.png` |

Evidence handling: the profile avatar was blurred and the OS status bar cropped in all screenshots, and no other member's account was captured. The Task 2 test tracks will be excluded from the owner's taste profile after the lab so that future recommendations are not skewed.

## Appendix B: References

- Spotify Support. *Exclude playlists or tracks from your taste profile.* https://support.spotify.com/ao-en/article/exclude-playlists-or-tracks-from-your-taste-profile/
- Spotify for Artists Support. *Songs recommended for Discovery Mode.* https://support.spotify.com/mw/artists/article/discovery-mode-recommended-songs/
- RouteNote (11 Dec 2023). *Spotify expands Discovery Mode, campaigns will feature in thematic playlists.* https://routenote.com/blog/spotify-expands-discovery-mode-mixes/
- TechCrunch (1 Oct 2025). *Spotify now lets you exclude tracks from your taste profile.* https://techcrunch.com/2025/10/01/spotify-now-lets-you-exclude-tracks-from-your-taste-profile-improving-recommendations/
