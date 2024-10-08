document.addEventListener('DOMContentLoaded', () => {
    const tierRankValues = {
        'UNRANKED': { 'IV': 900},        
        'IRON': { 'IV': 1000, 'III': 1100, 'II': 1200, 'I': 1300 },
        'BRONZE': { 'IV': 1400, 'III': 1500, 'II': 1600, 'I': 1700 },
        'SILVER': { 'IV': 1800, 'III': 1900, 'II': 2000, 'I': 2100 },
        'GOLD': { 'IV': 2200, 'III': 2300, 'II': 2400, 'I': 2500 },
        'PLATINUM': { 'IV': 2600, 'III': 2700, 'II': 2800, 'I': 2900 },
        'EMERALD' : { 'IV': 3000, 'III': 3100, 'II': 3200, 'I': 3300 },
        'DIAMOND': { 'IV': 3400, 'III': 3500, 'II': 3600, 'I': 3700 },
        'MASTER': { 'I': 3800 },
        'GRANDMASTER': { 'I': 3900 },
        'CHALLENGER': { 'I': 4000 }
    };

    const yLabelMap = {};
    Object.keys(tierRankValues).forEach(tier => {
        Object.keys(tierRankValues[tier]).forEach(rank => {
            yLabelMap[tierRankValues[tier][rank]] = `${tier} ${rank}`;
        });
    });

    const masterPlusTierRankValues = {
        'UNRANKED': { 'IV': -3100},        
        'GOLD': { 'IV': -1600, 'III': -1500, 'II': -1400, 'I': -1300 },
        'PLATINUM': { 'IV': -1200, 'III': -1100, 'II': -1000, 'I': -900 },
        'EMERALD' : { 'IV': -800, 'III': -700, 'II': -600, 'I': -500 },
        'DIAMOND': { 'IV': -400, 'III': -300, 'II': -200, 'I': -100 },
        'MASTER': { 'I': 0 },
        'GRANDMASTER': { 'I': 0 },
        'CHALLENGER': { 'I': 0 }
    };

    const masterPlusYLabelMap = {};
    Object.keys(masterPlusTierRankValues).forEach(tier => {
        Object.keys(masterPlusTierRankValues[tier]).forEach(rank => {
            masterPlusYLabelMap[masterPlusTierRankValues[tier][rank]] = `${tier} ${rank}`;
        });
    });

    function createChart(ctx, data, options) {
        return new Chart(ctx, {
            type: 'line',
            data: {
                datasets: data
            },
            options: options
        });
    }

    // Player Chart
    fetch('/data')
        .then(response => response.json())
        .then(data => {
            const playerCtx = document.getElementById('playerChart').getContext('2d');
            createChart(playerCtx, data, {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'hour',
                            displayFormats: {
                                hour: 'D/M, HH:mm'
                            },
                            tooltipFormat: 'D/M, HH:mm'
                        },
                        title: {
                            display: true,
                            text: 'Time'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Rank'
                        },
                        ticks: {
                            callback: function(value) {
                                return yLabelMap[value] || '';
                            },
                        },
                    }
                },
                plugins: {
                    title:{
                        display: true,
                        text: 'Player Chart'
                    },
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (context.parsed.y !== null) {
                                    label += `${context.raw.tier} ${context.raw.rank} ${context.raw.leaguePoints} LP`;
                                }
                                return label;
                            }
                        }
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                }
            });
        })
        .catch(error => console.error('Error fetching player data:', error));

    // Team Chart
    fetch('/team_data')
        .then(response => response.json())
        .then(data => {
            const teamCtx = document.getElementById('teamChart').getContext('2d');
            createChart(teamCtx, data, {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'hour',
                            displayFormats: {
                                hour: 'D/M, HH:mm'
                            },
                            tooltipFormat: 'D/M, HH:mm'
                        },
                        title: {
                            display: true,
                            text: 'Time'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Team Points'
                        }
                    }
                },
                plugins: {
                    title:{
                        display: true,
                        text: 'Team Chart'
                    },
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (context.parsed.y !== null) {
                                    label += Math.round(context.parsed.y);
                                }
                                return label;
                            }
                        }
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                }
            });
        })
        .catch(error => console.error('Error fetching team data:', error));
});