// Debug Console Helper - Paste this into browser console on your Weekly Chronicles site

(async function debugWeeklyChronicles() {
    console.log('🔍 Weekly Chronicles Debug Tool');
    console.log('================================');
    
    try {
        // Get the auth token from localStorage
        const token = localStorage.getItem('token');
        if (!token) {
            console.error('❌ No auth token found - please log in');
            return;
        }
        
        const headers = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };
        
        // Get backend URL from environment
        const backendUrl = window.location.origin + '/api';
        console.log('🌐 Backend URL:', backendUrl);
        
        // Fetch user info
        console.log('\n👤 Fetching current user info...');
        const userResponse = await fetch(`${backendUrl}/users/me`, { headers });
        const userData = await userResponse.json();
        console.log('User Data:', userData);
        
        // Fetch friends
        console.log('\n👥 Fetching friends list...');
        const friendsResponse = await fetch(`${backendUrl}/friends`, { headers });
        const friendsData = await friendsResponse.json();
        console.log('Friends:', friendsData);
        
        // Fetch my stories
        console.log('\n📚 Fetching your stories...');
        const storiesResponse = await fetch(`${backendUrl}/stories/my`, { headers });
        const storiesData = await storiesResponse.json();
        console.log('Your Stories:', storiesData);
        
        // Fetch current edition
        console.log('\n📰 Fetching weekly edition...');
        const editionResponse = await fetch(`${backendUrl}/editions/current`, { headers });
        const editionData = await editionResponse.json();
        console.log('Weekly Edition:', editionData);
        
        // Analysis
        console.log('\n🔍 ANALYSIS:');
        console.log('===============');
        console.log(`👥 Friends Count: ${userData.friends?.length || 0}`);
        console.log(`✅ Contributors Count: ${userData.contributors?.length || 0}`);
        console.log(`📝 Your Stories Count: ${storiesData.length}`);
        console.log(`📰 Edition Stories Count: ${editionData.stories?.length || 0}`);
        
        // Diagnose the problem
        if (userData.friends?.length > 0 && (!userData.contributors || userData.contributors.length === 0)) {
            console.error('❌ PROBLEM FOUND: You have friends but no contributors!');
            console.error('   This means friends are not being added as contributors.');
        } else if (userData.contributors?.length > 0 && editionData.stories?.length <= 1) {
            console.error('❌ PROBLEM FOUND: You have contributors but only seeing your own story!');
            console.error('   This means the weekly edition logic is not finding contributor stories.');
        } else if (userData.friends?.length === 0) {
            console.warn('⚠️ INFO: You have no friends added yet.');
        } else {
            console.log('✅ System appears to be working correctly!');
        }
        
        // Show detailed breakdown
        if (editionData.stories?.length > 0) {
            console.log('\n📄 Stories in your edition:');
            editionData.stories.forEach((story, index) => {
                console.log(`  ${index + 1}. "${story.title}" by ${story.author_name} (Week: ${story.week_of})`);
            });
        }
        
        // Show friend details
        if (friendsData.length > 0) {
            console.log('\n👥 Your friends:');
            friendsData.forEach((friend) => {
                console.log(`  - ${friend.full_name} (${friend.email})`);
            });
        }
        
        console.log('\n🎯 Copy this entire console output and share it with the developer!');
        
    } catch (error) {
        console.error('❌ Debug failed:', error);
    }
})();