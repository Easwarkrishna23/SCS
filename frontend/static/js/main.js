// Network Graph Visualization
class NetworkGraph {
    constructor(container) {
        this.container = container;
        this.svg = d3.select(container)
            .append('svg')
            .attr('width', '100%')
            .attr('height', '600px');
        this.simulation = null;
    }

    drawGraph(data) {
        const width = this.container.clientWidth;
        const height = 600;

        // Clear previous graph
        this.svg.selectAll("*").remove();

        // Create simulation
        this.simulation = d3.forceSimulation(data.nodes)
            .force("link", d3.forceLink(data.links).id(d => d.id))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2));

        // Draw links
        const links = this.svg.append("g")
            .selectAll("line")
            .data(data.links)
            .enter()
            .append("line")
            .attr("class", "link");

        // Draw nodes
        const nodes = this.svg.append("g")
            .selectAll("circle")
            .data(data.nodes)
            .enter()
            .append("circle")
            .attr("class", "node")
            .attr("r", 10)
            .call(this.dragBehavior());

        // Add node labels
        const labels = this.svg.append("g")
            .selectAll("text")
            .data(data.nodes)
            .enter()
            .append("text")
            .attr("class", "node-label")
            .text(d => d.username)
            .attr("dx", 15)
            .attr("dy", 5);

        // Update positions on tick
        this.simulation.on("tick", () => {
            links
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);

            nodes
                .attr("cx", d => d.x)
                .attr("cy", d => d.y);

            labels
                .attr("x", d => d.x)
                .attr("y", d => d.y);
        });
    }

    dragBehavior() {
        return d3.drag()
            .on("start", (event, d) => {
                if (!event.active) this.simulation.alphaTarget(0.3).restart();
                d.fx = d.x;
                d.fy = d.y;
            })
            .on("drag", (event, d) => {
                d.fx = event.x;
                d.fy = event.y;
            })
            .on("end", (event, d) => {
                if (!event.active) this.simulation.alphaTarget(0);
                d.fx = null;
                d.fy = null;
            });
    }
}

// Message Encryption/Decryption
class MessageCrypto {
    static async encrypt(message, publicKey) {
        const encoder = new TextEncoder();
        const data = encoder.encode(message);
        
        const encrypted = await window.crypto.subtle.encrypt(
            {
                name: "RSA-OAEP"
            },
            publicKey,
            data
        );
        
        return btoa(String.fromCharCode(...new Uint8Array(encrypted)));
    }

    static async decrypt(encryptedMessage, privateKey) {
        const encrypted = Uint8Array.from(atob(encryptedMessage), c => c.charCodeAt(0));
        
        const decrypted = await window.crypto.subtle.decrypt(
            {
                name: "RSA-OAEP"
            },
            privateKey,
            encrypted
        );
        
        const decoder = new TextDecoder();
        return decoder.decode(decrypted);
    }
}

// Notification Manager
class NotificationManager {
    constructor() {
        this.badge = document.getElementById('notification-badge');
        this.container = document.getElementById('notification-container');
    }

    updateBadge(count) {
        if (count > 0) {
            this.badge.textContent = count;
            this.badge.classList.remove('hidden');
        } else {
            this.badge.classList.add('hidden');
        }
    }

    addNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'notification-item fade-in';
        notification.innerHTML = `
            <div class="flex items-center p-4 bg-white shadow rounded-lg mb-2">
                <div class="flex-1">
                    <p class="text-sm text-gray-600">${message}</p>
                </div>
                <button class="ml-2 text-gray-400 hover:text-gray-600">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        this.container.prepend(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
}

// Initialize components
document.addEventListener('DOMContentLoaded', () => {
    // Initialize network graph if container exists
    const graphContainer = document.getElementById('network-graph');
    if (graphContainer) {
        const graph = new NetworkGraph(graphContainer);
        fetch('/api/network-data')
            .then(response => response.json())
            .then(data => graph.drawGraph(data));
    }

    // Initialize notification manager
    const notificationManager = new NotificationManager();
    
    // Setup WebSocket for real-time updates
    const ws = new WebSocket(`ws://${window.location.host}/ws`);
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'notification') {
            notificationManager.addNotification(data.message);
        }
    };
});