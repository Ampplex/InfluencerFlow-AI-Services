from supabase import create_client, Client

influencers_data = [
    {
        'id': 'e629ca4bc608e716cfec47b9c6858c6c',
        'metadata': {
            'bio': 'Join me on my acne journey',
            'email': 'mamata@example.com',
            'engagement_score': 0.05,
            'followers': 60700.0,
            'link': 'https://www.instagram.com/mamata/',
            'platform': 'Instagram',
            'username': 'mamata'
        },
        'page_content': 'bio: Join me on my acne journey, username: mamata, followers: 60700, link: https://www.instagram.com/mamata/, platform: Instagram'
    },
    {
        'id': 'cbe02b314c73c88faab11a4dd41eef3d',
        'metadata': {
            'bio': 'Beauty Blogger | Makeup & Skincare Influencer',
            'email': 'saba.naveed29@yahoo.com',
            'engagement_score': 0.02,
            'followers': 25000.0,
            'link': 'https://www.instagram.com/makeuplover.saba/',
            'platform': 'Instagram',
            'username': 'makeuplover.saba'
        },
        'page_content': 'bio: Beauty Blogger | Makeup & Skincare Influencer, username: makeuplover.saba, followers: 25000, link: https://www.instagram.com/makeuplover.saba/, platform: Instagram'
    },
    {
        'id': '05defb568e94343f72dcb352a41ee3a9',
        'metadata': {
            'bio': 'Tech and programming content influencer.',
            'email': 'ankeshpune@gmail.com',
            'engagement_score': 0.0,
            'followers': 260.0,
            'link': 'https://www.instagram.com/dev.ankeshkumar/',
            'platform': 'Instagram',
            'username': 'dev.ankeshkumar'
        },
        'page_content': 'bio: Tech and programming content influencer., username: dev.ankeshkumar, followers: 260, link: https://www.instagram.com/dev.ankeshkumar/, platform: Instagram'
    },
    {
        'id': '59a425b35fee4f9dfec4d4fd03381a23',
        'metadata': {
            'bio': 'Founder and CEO @Jdezbeauty | Beauty Vlogger',
            'email': 'makeupbyjh21@gmail.com',
            'engagement_score': 0.85,
            'followers': 1000000.0,
            'link': 'https://www.instagram.com/makeupbyjh/',
            'platform': 'Instagram',
            'username': 'makeupbyjh'
        },
        'page_content': 'bio: Founder and CEO @Jdezbeauty | Beauty Vlogger, username: makeupbyjh, followers: 1000000, link: https://www.instagram.com/makeupbyjh/, platform: Instagram'
    },
    {
        'id': '2962da38350c33714c9fbacc80472032',
        'metadata': {
            'bio': 'Beauty & Lifestyle Influencer',
            'email': 'jasleenarora996@gmail.com',
            'engagement_score': 3.79,
            'followers': 3200000.0,
            'link': 'https://www.instagram.com/missjasleenarora/',
            'platform': 'Instagram',
            'username': 'missjasleenarora'
        },
        'page_content': 'bio: Beauty & Lifestyle Influencer, username: missjasleenarora, followers: 3200000, link: https://www.instagram.com/missjasleenarora/, platform: Instagram'
    },
    {
        'id': 'c766c245347bc825213004dde13b7d6b',
        'metadata': {
            'bio': 'Self-taught MUA | Content Creator | Makeup Lover',
            'email': 'MakeupbyRositaa@gmail.com',
            'engagement_score': 0.07,
            'followers': 69000.0,
            'link': 'https://www.instagram.com/rositaaliana/',
            'platform': 'Instagram',
            'username': 'rositaaliana'
        },
        'page_content': 'bio: Self-taught MUA | Content Creator | Makeup Lover, username: rositaaliana, followers: 69000, link: https://www.instagram.com/rositaaliana/, platform: Instagram'
    },
    {
        'id': 'c0fccecd95a0238d13f075de5c78df6b',
        'metadata': {
            'bio': 'Beauty Content Creator | Business Developer AFRICA/EU/USA/UAE/UK',
            'email': 'maja@blazerinvestments.com',
            'engagement_score': 0.99,
            'followers': 1000000.0,
            'link': 'https://www.instagram.com/mayamiay/',
            'platform': 'Instagram',
            'username': 'mayamiay'
        },
        'page_content': 'bio: Beauty Content Creator | Business Developer AFRICA/EU/USA/UAE/UK, username: mayamiay, followers: 1000000, link: https://www.instagram.com/mayamiay/, platform: Instagram'
    },
    {
        'id': '0c62b22756db9c12c8edc50cda5fee6e',
        'metadata': {
            'bio': 'Your unfiltered skincare & beauty bestie',
            'email': 'rachel@hydrationceo.com',
            'engagement_score': 0.24,
            'followers': 200200.0,
            'link': 'https://www.instagram.com/rachelfinley/',
            'platform': 'Instagram',
            'username': 'rachelfinley'
        },
        'page_content': 'bio: Your unfiltered skincare & beauty bestie, username: rachelfinley, followers: 200200, link: https://www.instagram.com/rachelfinley/, platform: Instagram'
    },
    {
        'id': '5bb1a356d38031233da8ab75406c2130',
        'metadata': {
            'bio': 'Beauty & Fashion | Product Reviews',
            'email': 'makeuptutorialsx0x@outlook.com',
            'engagement_score': 1.2,
            'followers': 1000000.0,
            'link': 'https://www.instagram.com/makeuptutorialsx0x/',
            'platform': 'Instagram',
            'username': 'makeuptutorialsx0x'
        },
        'page_content': 'bio: Beauty & Fashion | Product Reviews, username: makeuptutorialsx0x, followers: 1000000, link: https://www.instagram.com/makeuptutorialsx0x/, platform: Instagram'
    },
    {
        'id': 'fa2b8bb688a6dc744b5894a6db533287',
        'metadata': {
            'bio': 'Beauty/Hair Content Creator | Founder of @aniluhome',
            'email': 'kaylani@chicinfluence.com',
            'engagement_score': 1.09,
            'followers': 1000000.0,
            'link': 'https://www.instagram.com/kaylani/',
            'platform': 'Instagram',
            'username': 'kaylani'
        },
        'page_content': 'bio: Beauty/Hair Content Creator | Founder of @aniluhome, username: kaylani, followers: 1000000, link: https://www.instagram.com/kaylani/, platform: Instagram'
    },
    {
        'id': 'a5dbb47da55d8cd5b1abdcfa178d703e',
        'metadata': {
            'bio': 'Development , Full Stack Coding',
            'email': 'ajaypun1976@gmail.com',
            'engagement_score': 0.03,
            'followers': 30555.0,
            'link': 'https://www.instagram.com/codewithankesh/',
            'platform': 'Instagram',
            'username': 'developer_ankesh'
        },
        'page_content': 'bio: Development , Full Stack Coding, username: developer_ankesh, followers: 30555, link: https://www.instagram.com/codewithankesh/, platform: Instagram'
    },
    {
        'id': 'c41eafb22beaa0c2d8cd7a43f8946794',
        'metadata': {
            'bio': 'Makeup Artist | Co-founder of Real Techniques',
            'email': 'sam@crumbagency.com',
            'engagement_score': 1.38,
            'followers': 1300000.0,
            'link': 'https://www.instagram.com/samchapman/',
            'platform': 'Instagram',
            'username': 'samchapman'
        },
        'page_content': 'bio: Makeup Artist | Co-founder of Real Techniques, username: samchapman, followers: 1300000, link: https://www.instagram.com/samchapman/, platform: Instagram'
    },
    {
        'id': 'fe436339214d1a8e4c2fece1d7ea83e1',
        'metadata': {
            'bio': 'Tech reviews, gadget comparisons, and tech news.',
            'email': 'contact@techburner.in',
            'engagement_score': 0.98,
            'followers': 800000.0,
            'link': 'https://www.instagram.com/thetechchap/',
            'platform': 'Instagram',
            'username': 'thetechchap'
        },
        'page_content': 'bio: Tech reviews, gadget comparisons, and tech news., username: thetechchap, followers: 800000, link: https://www.instagram.com/thetechchap/, platform: Instagram'
    },
    {
        'id': 'dcebb94cff0614ca95697f76f97f76dc',
        'metadata': {
            'bio': 'Owner @bangs.and.beard | Certified Freelance Makeup Artist',
            'email': 'shivangi.kochhar@example.com',
            'engagement_score': 0.06,
            'followers': 56000.0,
            'link': 'https://www.instagram.com/shivangikochhar/',
            'platform': 'Instagram',
            'username': 'shivangikochhar'
        },
        'page_content': 'bio: Owner @bangs.and.beard | Certified Freelance Makeup Artist, username: shivangikochhar, followers: 56000, link: https://www.instagram.com/shivangikochhar/, platform: Instagram'
    },
    {
        'id': '8801903e97641c909a90665778b111a5',
        'metadata': {
            'bio': 'Makeup Enthusiast | Content Creator',
            'email': 'weriitha.soloriio@example.com',
            'engagement_score': 0.06,
            'followers': 60000.0,
            'link': 'https://www.instagram.com/weriithasoloriio/',
            'platform': 'Instagram',
            'username': 'weriithasoloriio'
        },
        'page_content': 'bio: Makeup Enthusiast | Content Creator, username: weriithasoloriio, followers: 60000, link: https://www.instagram.com/weriithasoloriio/, platform: Instagram'
    },
    {
        'id': 'b27b4215eb747b18978e474f41ca9448',
        'metadata': {
            'bio': 'Spiritual & Motivational Speaker ॥ कृष्णं सदा सहायते ॥',
            'email': 'contact@iamjayakishori.com',
            'engagement_score': 9.62,
            'followers': 12300000.0,
            'link': 'https://www.instagram.com/iamjayakishori/',
            'platform': 'Instagram',
            'username': 'iamjayakishori'
        },
        'page_content': 'bio: Spiritual & Motivational Speaker ॥ कृष्णं सदा सहायते ॥, username: iamjayakishori, followers: 12300000, link: https://www.instagram.com/iamjayakishori/, platform: Instagram'
    },
    {
        'id': 'fa8ae4383ffc31111e17c3974845eefd',
        'metadata': {
            'bio': 'Tech and programming content.',
            'email': 'business@joma.io',
            'engagement_score': 2.7,
            'followers': 2280000.0,
            'link': 'https://www.youtube.com/@jomakaze',
            'platform': 'YouTube',
            'username': 'jomatech'
        },
        'page_content': 'bio: Tech and programming content., username: jomatech, followers: 2280000, link: https://www.youtube.com/@jomakaze, platform: YouTube'
    },
    {
        'id': '425b8e5b734f528d18d69acb8118c29b',
        'metadata': {
            'bio': 'Programming tutorials, coding challenges, and tech career advice.',
            'email': 'tim@123@gmail.com',
            'engagement_score': 1.55,
            'followers': 1500000.0,
            'link': 'https://www.instagram.com/techwithtim/',
            'platform': 'Instagram',
            'username': 'techwithtim'
        },
        'page_content': 'bio: Programming tutorials, coding challenges, and tech career advice., username: techwithtim, followers: 1500000, link: https://www.instagram.com/techwithtim/, platform: Instagram'
    },
    {
        'id': '34d67325b6e2dad309629ab18a3adb67',
        'metadata': {
            'bio': 'CEO/Chairman @vaynermedia | Creator @veefriends | Investor in FB, Venmo, Twitter',
            'email': 'gary@vaynermedia.com',
            'engagement_score': 8.84,
            'followers': 10400000.0,
            'link': 'https://www.instagram.com/garyvee/',
            'platform': 'Instagram',
            'username': 'garyvee'
        },
        'page_content': 'bio: CEO/Chairman @vaynermedia | Creator @veefriends | Investor in FB, Venmo, Twitter, username: garyvee, followers: 10400000, link: https://www.instagram.com/garyvee/, platform: Instagram'
    },
    {
        'id': '3ff5e5474c4217615480ca2d2fb32695',
        'metadata': {
            'bio': 'Freelance Makeup Artist | Melbourne',
            'email': 'amelia.webb@example.com',
            'engagement_score': 0.07,
            'followers': 65000.0,
            'link': 'https://www.instagram.com/makeupbyameliawebb/',
            'platform': 'Instagram',
            'username': 'makeupbyameliawebb'
        },
        'page_content': 'bio: Freelance Makeup Artist | Melbourne, username: makeupbyameliawebb, followers: 65000, link: https://www.instagram.com/makeupbyameliawebb/, platform: Instagram'
    },
    {
        'id': '4b24fec0c5b92cdacf51b954a16620b4',
        'metadata': {
            'bio': 'Gadget reviews, technology tips, app recommendations, and tech news.',
            'email': 'contact@technicalguruji.in',
            'engagement_score': 2.31,
            'followers': 2200000.0,
            'link': 'https://www.instagram.com/technicalguruji/',
            'platform': 'Instagram',
            'username': 'technicalguruji'
        },
        'page_content': 'bio: Gadget reviews, technology tips, app recommendations, and tech news., username: technicalguruji, followers: 2200000, link: https://www.instagram.com/technicalguruji/, platform: Instagram'
    },
    {
        'id': '187318db6436d814254511c0405c28f4',
        'metadata': {
            'bio': 'Makeup Artist | Soft & Glam Makeup | Bridal | Photo Shoots',
            'email': 'yohanabr00@gmail.com',
            'engagement_score': 0.03,
            'followers': 42000.0,
            'link': 'https://www.instagram.com/yohanarangelmua/',
            'platform': 'Instagram',
            'username': 'yohanarangelmua'
        },
        'page_content': 'bio: Makeup Artist | Soft & Glam Makeup | Bridal | Photo Shoots, username: yohanarangelmua, followers: 42000, link: https://www.instagram.com/yohanarangelmua/, platform: Instagram'
    },
    {
        'id': 'acc2123bca67c12a5d825ad785e4e456',
        'metadata': {
            'bio': 'Skincare | Makeup | Haircare | Biotechnologist | Licensed Skincare Consultant',
            'email': 'sneha.sen@honeycombmedia.in',
            'engagement_score': 0.3,
            'followers': 318100.0,
            'link': 'https://www.instagram.com/sneha.sen/',
            'platform': 'Instagram',
            'username': 'sneha.sen'
        },
        'page_content': 'bio: Skincare | Makeup | Haircare | Biotechnologist | Licensed Skincare Consultant, username: sneha.sen, followers: 318100, link: https://www.instagram.com/sneha.sen/, platform: Instagram'
    },
    {
        'id': 'f052fa03890f0211b6c8a53f1ed18efb',
        'metadata': {
            'bio': 'Known as Human Chameleon | Artist | Foodie',
            'email': 'promisetamang@gmail.com',
            'engagement_score': 1.21,
            'followers': 1000000.0,
            'link': 'https://www.instagram.com/promisetamang/',
            'platform': 'Instagram',
            'username': 'promisetamang'
        },
        'page_content': 'bio: Known as Human Chameleon | Artist | Foodie, username: promisetamang, followers: 1000000, link: https://www.instagram.com/promisetamang/, platform: Instagram'
    },
    {
        'id': '514fdbc474d62dee493b5d01190fc8fd',
        'metadata': {
            'bio': 'YouTube: Denitslava Makeup | TikTok: @denitslavaa',
            'email': 'denitslava@hotmail.com',
            'engagement_score': 0.92,
            'followers': 1000000.0,
            'link': 'https://www.instagram.com/denitslava/',
            'platform': 'Instagram',
            'username': 'denitslava'
        },
        'page_content': 'bio: YouTube: Denitslava Makeup | TikTok: @denitslavaa, username: denitslava, followers: 1000000, link: https://www.instagram.com/denitslava/, platform: Instagram'
    },
    {
        'id': 'ac09055ae143e7711af2ac95bdeea1f0',
        'metadata': {
            'bio': 'Makeup Artist | Content Creator',
            'email': 'steffy.sunny@example.com',
            'engagement_score': 0.49,
            'followers': 515900.0,
            'link': 'https://www.instagram.com/steffysunny/',
            'platform': 'Instagram',
            'username': 'steffysunny'
        },
        'page_content': 'bio: Makeup Artist | Content Creator, username: steffysunny, followers: 515900, link: https://www.instagram.com/steffysunny/, platform: Instagram'
    },
    {
        'id': '9f67ee9fed8d05f881ebc3a2c39ed7a0',
        'metadata': {
            'bio': 'Makeup Artist | Masterclasses Available',
            'email': 'info@nikkimakeup.com',
            'engagement_score': 1.76,
            'followers': 2100000.0,
            'link': 'https://www.instagram.com/nikkimakeup/',
            'platform': 'Instagram',
            'username': 'nikkimakeup'
        },
        'page_content': 'bio: Makeup Artist | Masterclasses Available, username: nikkimakeup, followers: 2100000, link: https://www.instagram.com/nikkimakeup/, platform: Instagram'
    },
    {
        'id': 'f05bd211238babc6e53dc2b433e12d26',
        'metadata': {
            'bio': 'Personal coach, monk, lifestyle & motivational strategist, author',
            'email': 'gaurgopaldas@gmail.com',
            'engagement_score': 10.0,
            'followers': 8700000.0,
            'link': 'https://www.instagram.com/gaurgopaldas/',
            'platform': 'Instagram',
            'username': 'gaurgopaldas'
        },
        'page_content': 'bio: Personal coach, monk, lifestyle & motivational strategist, author, username: gaurgopaldas, followers: 8700000, link: https://www.instagram.com/gaurgopaldas/, platform: Instagram'
    },
    {
        'id': '571868742a924f3d8823f27ef0258e42',
        'metadata': {
            'bio': 'Fashion, beauty, life',
            'email': 'aashna@thesnobjournal.com',
            'engagement_score': 0.94,
            'followers': 1000000.0,
            'link': 'https://www.instagram.com/aashnashroff/',
            'platform': 'Instagram',
            'username': 'aashnashroff'
        },
        'page_content': 'bio: Fashion, beauty, life, username: aashnashroff, followers: 1000000, link: https://www.instagram.com/aashnashroff/, platform: Instagram'
    },
    {
        'id': 'b1c73322eca15b326bff9d7463b99035',
        'metadata': {
            'bio': 'Professional Makeup Artist | Based in Mumbai/Patna',
            'email': 'nikita.bhardwaj@example.com',
            'engagement_score': 0.46,
            'followers': 520800.0,
            'link': 'https://www.instagram.com/nikitabhardwaj00/',
            'platform': 'Instagram',
            'username': 'nikitabhardwaj00'
        },
        'page_content': 'bio: Professional Makeup Artist | Based in Mumbai/Patna, username: nikitabhardwaj00, followers: 520800, link: https://www.instagram.com/nikitabhardwaj00/, platform: Instagram'
    },
    {
        'id': '91f6e5141b3df817716ef6a37dc14d94',
        'metadata': {
            'bio': 'Founder of @hindashcosmetics',
            'email': 'info@hindash.com',
            'engagement_score': 1.7,
            'followers': 1500000.0,
            'link': 'https://www.instagram.com/hindash/',
            'platform': 'Instagram',
            'username': 'hindash'
        },
        'page_content': 'bio: Founder of @hindashcosmetics, username: hindash, followers: 1500000, link: https://www.instagram.com/hindash/, platform: Instagram'
    },
    {
        'id': '11c7bcf5676d2512035faa548438c952',
        'metadata': {
            'bio': 'Makeup Artist & Content Creator',
            'email': 'contact@daniellemarcan.co.uk',
            'engagement_score': 1.94,
            'followers': 1700000.0,
            'link': 'https://www.instagram.com/daniellemarcan/',
            'platform': 'Instagram',
            'username': 'daniellemarcan'
        },
        'page_content': 'bio: Makeup Artist & Content Creator, username: daniellemarcan, followers: 1700000, link: https://www.instagram.com/daniellemarcan/, platform: Instagram'
    },
    {
        'id': '4b3e78d497024ff22c15c76d29e8d1b0',
        'metadata': {
            'bio': 'Celebrity Makeup Artist',
            'email': 'bookings@maneaddicts.com',
            'engagement_score': 2.79,
            'followers': 2300000.0,
            'link': 'https://www.instagram.com/maryphillips/',
            'platform': 'Instagram',
            'username': 'maryphillips'
        },
        'page_content': 'bio: Celebrity Makeup Artist, username: maryphillips, followers: 2300000, link: https://www.instagram.com/maryphillips/, platform: Instagram'
    },
    {
        'id': '44417a5bde5941e5d61e799a3383240e',
        'metadata': {
            'bio': 'Founder & Creative Director of Natasha Denona Cosmetics',
            'email': 'info@natashadenona.com',
            'engagement_score': 1.68,
            'followers': 1500000.0,
            'link': 'https://www.instagram.com/natashadenona/',
            'platform': 'Instagram',
            'username': 'natashadenona'
        },
        'page_content': 'bio: Founder & Creative Director of Natasha Denona Cosmetics, username: natashadenona, followers: 1500000, link: https://www.instagram.com/natashadenona/, platform: Instagram'
    },
    {
        'id': 'b2e27a01c7b3b7456f5c47ff11e566f9',
        'metadata': {
            'bio': 'Founder of Lisa Eldridge Makeup | NY Times Bestselling Author',
            'email': 'info@lisaeldridge.com',
            'engagement_score': 1.67,
            'followers': 2000000.0,
            'link': 'https://www.instagram.com/lisaeldridgemakeup/',
            'platform': 'Instagram',
            'username': 'lisaeldridgemakeup'
        },
        'page_content': 'bio: Founder of Lisa Eldridge Makeup | NY Times Bestselling Author, username: lisaeldridgemakeup, followers: 2000000, link: https://www.instagram.com/lisaeldridgemakeup/, platform: Instagram'
    }
]

    # Replace with your Supabase project credentials
SUPABASE_URL = "https://eepxrnqcefpvzxqkpjaw.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVlcHhybnFjZWZwdnp4cWtwamF3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDg2MzIzNDgsImV4cCI6MjA2NDIwODM0OH0.zTsgRk2c8zdO0SnQBI9CicH_NodH_C9duSdbwojAKBQ"

    # Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Print formatted data for verification
for influencer in influencers_data:
    print(f"Id: {influencer['id']}")
    print(f"Username: {influencer['metadata']['username']}")
    print(f"Platform: {influencer['metadata']['platform']}")
    print(f"Followers: {int(influencer['metadata']['followers']):,}")
    print(f"Engagement Score: {influencer['metadata']['engagement_score']}")
    print(f"Bio: {influencer['metadata']['bio']}")
    print("-" * 50)


    # Sample influencer data
    influencer_data = {
        'id': influencer['id'],
        "influencer_username": influencer['metadata']['username'],
        "influencer_email": influencer['metadata']['email'],
        "platforms": influencer['metadata']['platform'],
        "influencer_followers": int(influencer['metadata']['followers']),
        "bio": influencer['metadata']['bio'],
        'phone_num': None
    }

    # Insert into 'influencers' table
    response = supabase.table("influencers").insert(influencer_data).execute()

    # Print result
    print(response.data)