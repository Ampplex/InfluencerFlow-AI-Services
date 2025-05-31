mock_influencers = [
    {
        'username': 'fitness_julia',
        'followers': 980000,
        'posts': 340,
        'email': 'julia.fit@example.com',
        'bio': 'Fitness enthusiast | Coach | Vegan 🌱',
        'platform': 'Instagram'
    },
    {
        'username': 'techwithryan',
        'followers': 1150000,
        'posts': 612,
        'email': 'ryan.tech@example.com',
        'bio': 'Tech tutorials, reviews, and gadgets 📱💻',
        'platform': 'YouTube'
    },
    {
        'username': 'makeupbyliya',
        'followers': 720000,
        'posts': 455,
        'email': 'liya.beauty@example.com',
        'bio': 'Beauty Blogger | Makeup tutorials 💄✨',
        'platform': 'Instagram'
    },
    {
        'username': 'travel_vik',
        'followers': 860000,
        'posts': 580,
        'email': 'vik.travels@example.com',
        'bio': 'Travel the world with me 🌍✈️',
        'platform': 'Instagram'
    },
    {
        'username': 'cookingwithnina',
        'followers': 950000,
        'posts': 302,
        'email': 'nina.cooks@example.com',
        'bio': 'Easy recipes & kitchen hacks 👩‍🍳🍲',
        'platform': 'YouTube'
    },
    {
        'username': 'thebookcrate',
        'followers': 430000,
        'posts': 215,
        'email': 'books.crate@example.com',
        'bio': 'Reviews, recs & reads 📚✨',
        'platform': 'Instagram'
    },
    {
        'username': 'fashionablychloe',
        'followers': 1200000,
        'posts': 700,
        'email': 'chloe.style@example.com',
        'bio': 'NYC Fashionista | Collabs DM 📩',
        'platform': 'Instagram'
    },
    {
        'username': 'gamingnova',
        'followers': 1750000,
        'posts': 980,
        'email': 'nova.games@example.com',
        'bio': 'Let’s play! Daily gaming videos 🎮🔥',
        'platform': 'YouTube'
    },
    {
        'username': 'plantloverz',
        'followers': 390000,
        'posts': 190,
        'email': 'plantsforall@example.com',
        'bio': 'Indoor jungle creator 🌱🏡',
        'platform': 'Instagram'
    },
    {
        'username': 'codingwithsam',
        'followers': 620000,
        'posts': 88,
        'email': 'sam.codes@example.com',
        'bio': 'Learn to code | Python | JS 💻🚀',
        'platform': 'YouTube'
    },
    {
        'username': 'dailydoodleart',
        'followers': 310000,
        'posts': 612,
        'email': 'doodle.art@example.com',
        'bio': 'Sketching stories one frame at a time ✏️',
        'platform': 'Instagram'
    },
    {
        'username': 'mindsetmatters',
        'followers': 540000,
        'posts': 265,
        'email': 'positivityzone@example.com',
        'bio': 'Mental health | Daily affirmations 💬🧠',
        'platform': 'Instagram'
    },
    {
        'username': 'sneakerbeast101',
        'followers': 890000,
        'posts': 408,
        'email': 'sneaker.king@example.com',
        'bio': 'Sneaker reviews | Streetwear drip 👟🔥',
        'platform': 'YouTube'
    },
    {
        'username': 'mommycrafts',
        'followers': 270000,
        'posts': 200,
        'email': 'crafty.mom@example.com',
        'bio': 'DIY Projects & Parenting hacks ✂️🍼',
        'platform': 'Instagram'
    },
    {
        'username': 'historydecoded',
        'followers': 510000,
        'posts': 175,
        'email': 'hist.geek@example.com',
        'bio': 'Uncovering the past 🔍📜',
        'platform': 'YouTube'
    },
    {
        'username': 'comedyplug',
        'followers': 930000,
        'posts': 750,
        'email': 'comedy.plug@example.com',
        'bio': 'Daily sketches that make you LOL 😂',
        'platform': 'Instagram'
    },
    {
        'username': 'fitnessfabian',
        'followers': 1200000,
        'posts': 411,
        'email': 'fabian.fit@example.com',
        'bio': 'Bodybuilding | Nutrition | Coaching 💪',
        'platform': 'Instagram'
    },
    {
        'username': 'techsaga',
        'followers': 810000,
        'posts': 503,
        'email': 'techsaga@example.com',
        'bio': 'Unboxing & gadget reviews 🎧📦',
        'platform': 'YouTube'
    },
    {
        'username': 'vocalvibes',
        'followers': 420000,
        'posts': 112,
        'email': 'music.vibes@example.com',
        'bio': 'Singing covers and originals 🎤🎵',
        'platform': 'YouTube'
    },
    {
        'username': 'culinarycrush',
        'followers': 770000,
        'posts': 380,
        'email': 'foodcrush@example.com',
        'bio': 'Gourmet dishes & food photography 🍽️📸',
        'platform': 'Instagram'
    },
    {
        'username': 'eco_emily',
        'followers': 340000,
        'posts': 218,
        'email': 'greenemily@example.com',
        'bio': 'Sustainable living & eco hacks ♻️🌍',
        'platform': 'Instagram'
    },
    {
        'username': 'lifewithzane',
        'followers': 650000,
        'posts': 290,
        'email': 'zanelife@example.com',
        'bio': 'Lifestyle, vlogs & motivation 💫',
        'platform': 'YouTube'
    },
    {
        'username': 'gadgetbyteindia',
        'followers': 1350000,
        'posts': 904,
        'email': 'gadgetbyte@example.com',
        'bio': 'Tech news | Unboxings | Reviews 🇮🇳📱',
        'platform': 'YouTube'
    },
    {
        'username': 'thepetgram',
        'followers': 710000,
        'posts': 550,
        'email': 'furryfriends@example.com',
        'bio': 'Cute pets and their stories 🐾🐶',
        'platform': 'Instagram'
    },
    {
        'username': 'luxurylivingnow',
        'followers': 460000,
        'posts': 244,
        'email': 'luxliv@example.com',
        'bio': 'Luxury homes, cars & watches ⌚🏠🚘',
        'platform': 'Instagram'
    },
    {
        'username': 'devdaily',
        'followers': 520000,
        'posts': 193,
        'email': 'devdaily@example.com',
        'bio': 'Web dev tips and projects 💻🔥',
        'platform': 'YouTube'
    },
    {
        'username': 'streetfoodhunter',
        'followers': 990000,
        'posts': 612,
        'email': 'streeteats@example.com',
        'bio': 'Exploring street food globally 🌍🍢',
        'platform': 'YouTube'
    },
    {
        'username': 'zenwithava',
        'followers': 330000,
        'posts': 280,
        'email': 'ava.yoga@example.com',
        'bio': 'Yoga, meditation, and wellness 🧘‍♀️💚',
        'platform': 'Instagram'
    },
    {
        'username': 'laughterfuel',
        'followers': 1180000,
        'posts': 744,
        'email': 'laughfuel@example.com',
        'bio': 'Comedy reels that’ll make your day 😂🔥',
        'platform': 'Instagram'
    },
    {
        'username': 'diydesignzone',
        'followers': 610000,
        'posts': 445,
        'email': 'diyzone@example.com',
        'bio': 'Crafts | Home decor | Tutorials 🎨🏠',
        'platform': 'YouTube'
    },
    {
        'username': 'motivatemindset',
        'followers': 390000,
        'posts': 208,
        'email': 'motivation@example.com',
        'bio': 'Success quotes & inspiration 🌟💭',
        'platform': 'Instagram'
    },
    {
        'username': 'codingtutor',
        'followers': 870000,
        'posts': 120,
        'email': 'code.tutor@example.com',
        'bio': 'Coding lessons made simple 🧑‍💻📘',
        'platform': 'YouTube'
    },
    {
        'username': 'glamgurl',
        'followers': 1050000,
        'posts': 496,
        'email': 'glamgirl@example.com',
        'bio': 'Beauty, lifestyle, and fashion 💅👗',
        'platform': 'Instagram'
    },
    {
        'username': 'indie_beats',
        'followers': 720000,
        'posts': 138,
        'email': 'beats.indie@example.com',
        'bio': 'Indie music & underground artists 🎶🌌',
        'platform': 'YouTube'
    },
]

coding_influencers = [
        {
        'username': 'codewithnina',
        'followers': 850000,
        'posts': 220,
        'email': 'nina.code@example.com',
        'bio': 'Teaching Python and full-stack development 👩‍💻💡 | Building dev confidence!',
        'platform': 'YouTube'
    },
    {
        'username': 'dev_dave',
        'followers': 430000,
        'posts': 185,
        'email': 'dave.dev@example.com',
        'bio': 'React, Node.js & coding tutorials 🧑‍💻 | Let’s build together!',
        'platform': 'Instagram'
    },
    {
        'username': 'tech_simplified',
        'followers': 610000,
        'posts': 152,
        'email': 'contact@techsimplified.io',
        'bio': 'Simplifying system design, DSA & interview prep 📊🎯',
        'platform': 'YouTube'
    },
    {
        'username': 'coder.queen',
        'followers': 970000,
        'posts': 310,
        'email': 'queenofcode@example.com',
        'bio': 'Software engineer @FAANG | Inspiring women in tech 👑💻',
        'platform': 'TikTok'
    },
    {
        'username': 'debuglife',
        'followers': 520000,
        'posts': 176,
        'email': 'hello@debuglife.dev',
        'bio': 'Relatable dev memes, tips & open source grind 💬🔥',
        'platform': 'Instagram'
    },
    {
        'username': 'thebughunter',
        'followers': 305000,
        'posts': 142,
        'email': 'bughunter@example.com',
        'bio': 'Cybersecurity & ethical hacking 🔐 | Bug bounty journey',
        'platform': 'YouTube'
    },
    {
        'username': 'ai.alina',
        'followers': 440000,
        'posts': 99,
        'email': 'alina.ai@example.com',
        'bio': 'ML models & GenAI breakdowns 🤖🧠 | Research meets real world',
        'platform': 'LinkedIn'
    },
    {
        'username': 'fullstackfred',
        'followers': 690000,
        'posts': 204,
        'email': 'fred.codes@example.com',
        'bio': 'Daily coding challenges, backend systems, and coffee ☕💾',
        'platform': 'Instagram'
    },
    {
        'username': 'techy_terry',
        'followers': 510000,
        'posts': 178,
        'email': 'terry@techbytes.io',
        'bio': 'Short-form tutorials on TypeScript, APIs & cloud ☁️⚡',
        'platform': 'TikTok'
    },
    {
        'username': 'dsa_mastery',
        'followers': 770000,
        'posts': 240,
        'email': 'dsa.master@example.com',
        'bio': 'Crack coding interviews with daily DSA problems 🧠🧩',
        'platform': 'YouTube'
    }
]