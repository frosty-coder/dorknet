document.addEventListener('DOMContentLoaded', () => {
    // Authentication Toggle
    const loginToggle = document.getElementById('login-toggle');
    const signupToggle = document.getElementById('signup-toggle');
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');
    const authContainer = document.getElementById('auth-container');
    const mainApp = document.getElementById('main-app');
    const errorMessage = document.getElementById('error-message');

    // Navigation
    const navButtons = document.querySelectorAll('.nav-btn');
    const sections = ['chat-section', 'marketplace-section', 'community-section', 'games-section'];

    // Authentication Toggling
    loginToggle.addEventListener('click', () => {
        loginForm.classList.remove('hidden');
        signupForm.classList.add('hidden');
        loginToggle.classList.add('bg-blue-600');
        signupToggle.classList.remove('bg-purple-600');
    });

    signupToggle.addEventListener('click', () => {
        signupForm.classList.remove('hidden');
        loginForm.classList.add('hidden');
        signupToggle.classList.add('bg-purple-600');
        loginToggle.classList.remove('bg-blue-600');
    });

    // Login Handler
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('login-username').value;
        const password = document.getElementById('login-password').value;

        try {
            const response = await fetch('/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();
            if (data.success) {
                authContainer.classList.add('hidden');
                mainApp.classList.remove('hidden');
                document.getElementById('username-display').textContent = username;
            } else {
                errorMessage.textContent = data.message;
            }
        } catch (error) {
            errorMessage.textContent = 'Login failed. Please try again.';
        }
    });

    // Signup Handler
    signupForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('signup-username').value;
        const password = document.getElementById('signup-password').value;
        const confirmPassword = document.getElementById('signup-confirm-password').value;

        if (password !== confirmPassword) {
            errorMessage.textContent = 'Passwords do not match!';
            return;
        }

        try {
            const response = await fetch('/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();
            if (data.success) {
                authContainer.classList.add('hidden');
                mainApp.classList.remove('hidden');
                document.getElementById('username-display').textContent = username;
            } else {
                errorMessage.textContent = data.message;
            }
        } catch (error) {
            errorMessage.textContent = 'Signup failed. Please try again.';
        }
    });

    // Navigation Handler
    navButtons.forEach(button => {
        button.addEventListener('click', () => {
            const sectionId = button.getAttribute('data-section') + '-section';

            // Hide all sections
            sections.forEach(section => {
                document.getElementById(section).classList.add('hidden');
            });

            // Show selected section
            document.getElementById(sectionId).classList.remove('hidden');
        });
    });

    // Marketplace Item Listing
    const listItemBtn = document.getElementById('list-item');
    const marketplaceItems = document.getElementById('marketplace-items');

    listItemBtn.addEventListener('click', () => {
        const itemName = document.getElementById('item-name').value;
        const itemPrice = document.getElementById('item-price').value;
        const itemCategory = document.getElementById('item-category').value;

        if (itemName && itemPrice) {
            const itemElement = document.createElement('div');
            itemElement.classList.add('bg-gray-100', 'p-4', 'rounded');
            itemElement.innerHTML = `
                <h4 class="font-bold">${itemName}</h4>
                <p>Price: $${itemPrice}</p>
                <p>Category: ${itemCategory}</p>
                <button class="mt-2 bg-green-500 text-white px-3 py-1 rounded">Buy</button>
            `;
            marketplaceItems.appendChild(itemElement);

            // Reset form
            document.getElementById('item-name').value = '';
            document.getElementById('item-price').value = '';
        }
    });

    // Community Post Creation
    const createPostBtn = document.getElementById('create-post');
    const communityPosts = document.getElementById('community-posts');

    createPostBtn.addEventListener('click', () => {
        const postContent = document.getElementById('post-content').value;

        if (postContent) {
            const postElement = document.createElement('div');
            postElement.classList.add('bg-gray-100', 'p-4', 'rounded');
            postElement.innerHTML = `
                <p>${postContent}</p>
                <div class="flex mt-2 space-x-4">
                    <button class="text-green-500">👍 Like</button>
                    <button class="text-red-500">👎 Dislike</button>
                    <button class="text-blue-500">💬 Comment</button>
                </div>
            `;
            communityPosts.prepend(postElement);

            // Reset textarea
            document.getElementById('post-content').value = '';
        }
    });

    // Game Collection Fetching (Mock Poki-like integration)
    const fetchGames = async () => {
        const gameCollection = document.getElementById('game-collection');
        const mockGames = [
            { name: 'Run 3', url: 'https://example.com/run3' },
            { name: 'Happy Wheels', url: 'https://example.com/happywheels' },
            { name: 'Fireboy and Watergirl', url: 'https://example.com/fireboywatergirl' },
            { name: 'Slope', url: 'https://example.com/slope' },
            { name: 'Cut the Rope', url: 'https://example.com/cuttherope' },
            { name: 'Minecraft Classic', url: 'https://example.com/minecraftclassic' }
        ];

        mockGames.forEach(game => {
            const gameElement = document.createElement('div');
            gameElement.classList.add('bg-white', 'p-4', 'rounded', 'shadow');
            gameElement.innerHTML = `
                <h3 class="font-bold mb-2">${game.name}</h3>
                <a href="${game.url}" target="_blank" class="bg-blue-500 text-white px-3 py-1 rounded">Play</a>
            `;
            gameCollection.appendChild(gameElement);
        });
    };
    fetchGames();

    // Logout Handler
    const logoutBtn = document.getElementById('logout-btn');
    logoutBtn.addEventListener('click', () => {
        mainApp.classList.add('hidden');
        authContainer.classList.remove('hidden');
        document.getElementById('username-display').textContent = '';
    });
});