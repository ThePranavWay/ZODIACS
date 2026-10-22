"""Integrated launch/theme/end regressions, isolated local fixture from test_app."""
from pathlib import Path
import hashlib,json,unittest
from unittest.mock import patch
import test_app as base
from app import app,ZODIAC_EVENT_END_AT,ZODIAC_EVENT_START_AT
ROOT=Path(__file__).resolve().parents[1]

class EventPageTests(unittest.TestCase):
    def setUp(self):base.EventTests.setUp(self)
    def member(self,*args,**kwargs):return base.EventTests.member(self,*args,**kwargs)
    def test_main_routes_and_assets(self):
        with patch('app.time.time',return_value=ZODIAC_EVENT_START_AT-1):
            for path in ['/','/play','/play.html','/event-ended','/event-ended.html','/zodiac-theme.js','/zodiac-theme.css','/theme-fonts/inter-300-700.woff2','/mission.css','/zodiac-seeker-brochure.pdf','/initial-evidence-reddit-post.png','/theme-fonts/cinzel-700-900.woff2','/letter','/letter.html','/document-z-k','/testemonies','/level-session.js','/level1-connect.js','/level2-connect.js','/level3-connect.js']:
                self.assertEqual(self.client.get(path).status_code,200,path)
    def test_theme_installed_on_all_nonlevel_pages(self):
        for name in ['index','play','organizer','event-ended']:
            text=(ROOT/'public'/f'{name}.html').read_text()
            self.assertEqual(text.count('src="/zodiac-theme.js?v=1"'),1)
            self.assertEqual(text.count('href="/zodiac-theme.css?v=1"'),1)
            self.assertLess(text.index('src="/zodiac-theme.js?v=1"'),text.lower().index('</head>'))
    def test_preservation_manifest(self):
        for path,digest in json.loads((ROOT/'preservation-sha256.json').read_text()).items():
            self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),digest,path)
    def test_old_level_files_removed_new_letter_level_connected(self):
        for name in ['attacks','investigate','next','later']:
            self.assertFalse((ROOT/'public'/f'{name}.html').exists(),name)
            self.assertEqual(self.client.get('/'+name).status_code,404,name)
        letter=(ROOT/'public/letter.html').read_text()
        # Organizer instruction: the Level 1 code stays in the supplied page
        # source for students to find; connection is via external scripts only.
        self.assertIn('ACCESS_KEY',letter)
        self.assertIn('/level-session.js',letter)
        self.assertIn('/level1-connect.js',letter)
        connect1=(ROOT/'public/level1-connect.js').read_text()
        self.assertIn('ZodiacLevels.unlock',connect1);self.assertIn('ZodiacLevels.view',connect1)
        connect2=(ROOT/'public/level2-connect.js').read_text()
        self.assertIn("closest('#yes')",connect2);self.assertIn("location.assign('/testemonies')",connect2)
        connect3=(ROOT/'public/level3-connect.js').read_text()
        self.assertIn('ZodiacLevels.verify',connect3)
        testimonies=(ROOT/'public/testemonies.html').read_text()
        self.assertIn('https://jumpshare.com/s/i4tsiaCJKy7ZSG3evEoj',testimonies)
        self.assertIn('▶ LISTEN AUDIO ↗',testimonies)
        self.assertIn('LISTEN OR DOWNLOAD THE AUDIO ON Jumpshare',testimonies)
        self.assertIn('target="_blank"',testimonies)
        self.assertNotIn('AUDIO EVIDENCE PENDING',testimonies)
        for name,marker in [('document-z-k.html','/level2-connect.js'),('testemonies.html','/level3-connect.js')]:
            self.assertIn(marker,(ROOT/'public'/name).read_text())
        with patch('app.time.time',return_value=ZODIAC_EVENT_START_AT-1):
            for path in ['/letter','/document-z-k','/testemonies','/level-session.js','/level1-connect.js','/level2-connect.js','/level3-connect.js']:
                self.assertEqual(self.client.get(path).status_code,200,path)
        play=(ROOT/'public/play.html').read_text()
        self.assertIn('all seven levels',play)
        for route in ['/letter','/document-z-k','/testemonies']:
            self.assertNotIn(route,play)
    def test_mission_pages_and_brochure_present(self):
        play=(ROOT/'public/play.html').read_text()
        for marker in ['page-briefing','page-objectives','page-initial','Mission Briefing','Mission Objectives','Initial Evidence','20 December 1968 and 11 October 1969','initial-evidence-reddit-post.png','/mission.css']:
            self.assertIn(marker,play)
        launch=(ROOT/'public/index.html').read_text()
        self.assertIn('/zodiac-seeker-brochure.pdf',launch)
        self.assertIn('VIEW BROCHURE',launch)
        self.assertNotIn('id="support"',launch)
        self.assertNotIn('Four levels. One investigation.',launch)
        self.assertIn('aria-label="The Zodiac Seeker"',launch)
        self.assertIn('class="title-the">THE</span>',launch)
        script=(ROOT/'public/app.js').read_text()
        self.assertIn("'Registration is currently closed'",script)
        self.assertIn('scrollIntoView',script)
    def test_launch_and_close_guards_present(self):
        launch=(ROOT/'public/index.html').read_text()
        self.assertIn('2026-11-01T00:00:00+05:30',launch)
        self.assertIn('1 NOVEMBER',launch)
        self.assertNotIn('2026-10-24',launch)
        self.assertIn('window.ZodiacEventClosed === true',launch)
        self.assertIn('event-redirect.js',launch)
        self.assertIn('event-redirect.js',(ROOT/'public/play.html').read_text())
        self.assertEqual(ZODIAC_EVENT_START_AT,1793471400)
        self.assertEqual(ZODIAC_EVENT_END_AT,1794551400)
    def test_root_redirects_to_play_only_after_31st_october_night(self):
        with patch('app.time.time',return_value=ZODIAC_EVENT_START_AT-1):
            self.assertEqual(self.client.get('/').status_code,200)
            self.assertEqual(self.client.get('/index.html').status_code,200)
            self.assertFalse(self.client.get('/api/event-clock').json['started'])
        with patch('app.time.time',return_value=ZODIAC_EVENT_START_AT):
            for path in ['/','/index.html']:
                r=self.client.get(path);self.assertEqual(r.status_code,302);self.assertEqual(r.headers['Location'],'/play')
            self.assertTrue(self.client.get('/api/event-clock').json['started'])
            for path in ['/play','/letter','/document-z-k','/testemonies']:
                self.assertEqual(self.client.get(path).status_code,200,path)
    def test_server_clock_boundary(self):
        for now,ended in [(ZODIAC_EVENT_END_AT-1,False),(ZODIAC_EVENT_END_AT,True)]:
            with patch('app.time.time',return_value=now):
                r=self.client.get('/api/event-clock')
                self.assertEqual(r.json['ended'],ended);self.assertEqual(r.json['server_time'],now)
                self.assertIn('no-store',r.headers['Cache-Control'])
    def test_game_routes_open_before_closing(self):
        with patch('app.time.time',return_value=ZODIAC_EVENT_END_AT-1):
            for path in ['/play','/play.html','/letter']:self.assertEqual(self.client.get(path).status_code,200)
            for path in ['/','/index.html']:
                r=self.client.get(path);self.assertEqual(r.status_code,302);self.assertEqual(r.headers['Location'],'/play')
    def test_game_routes_redirect_at_exact_deadline(self):
        with patch('app.time.time',return_value=ZODIAC_EVENT_END_AT):
            for path in ['/','/index.html','/play','/play.html']:
                r=self.client.get(path);self.assertEqual(r.status_code,302);self.assertEqual(r.headers['Location'],'/event-ended')
    def test_closed_event_rejects_register_and_answers(self):
        with patch('app.time.time',return_value=ZODIAC_EVENT_END_AT):
            for path in ['/api/register','/api/levels/1/submit','/api/levels/4/submit']:
                r=self.client.post(path,json={});self.assertEqual(r.status_code,410);self.assertTrue(r.json['event_ended'])
    def test_results_and_notes_remain_authenticated_after_close(self):
        with patch('app.time.time',return_value=ZODIAC_EVENT_END_AT):
            self.assertEqual(self.client.get('/api/leaderboard').status_code,401)
            self.assertEqual(self.client.get('/api/notes').status_code,401)
            self.assertEqual(self.client.get('/organizer').status_code,200)
            self.assertEqual(self.client.get('/event-ended').status_code,200)
    def test_existing_participant_keeps_notes_and_results_after_close(self):
        result=base.EventTests.register(self);self.assertEqual(result.status_code,201)
        with patch('app.time.time',return_value=ZODIAC_EVENT_END_AT):
            self.assertEqual(self.client.get('/api/leaderboard').status_code,200)
            r=self.client.post('/api/notes',json={'body':'Closing notebook test','version':0})
            self.assertEqual(r.status_code,200)
            self.assertEqual(self.client.get('/api/notes').json['body'],'Closing notebook test')
    def test_no_missing_advanced_import(self):
        self.assertNotIn('from advanced import',(ROOT/'app.py').read_text())
        self.assertEqual(self.client.get('/api/config').json['version'],4)
