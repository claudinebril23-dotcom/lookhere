django.jQuery(document).ready(function($) {
    const colorMap = {
        'red': '#FF0000',
        'blue': '#0000FF',
        'green': '#008000',
        'yellow': '#FFFF00',
        'orange': '#FFA500',
        'purple': '#800080',
        'pink': '#FFC0CB',
        'black': '#000000',
        'white': '#FFFFFF',
        'gray': '#808080',
        'grey': '#808080',
        'brown': '#A52A2A',
        'navy': '#000080',
        'teal': '#008080',
        'lime': '#00FF00',
        'cyan': '#00FFFF',
        'magenta': '#FF00FF',
        'maroon': '#800000',
        'olive': '#808000',
        'silver': '#C0C0C0',
        'gold': '#FFD700',
        'coral': '#FF7F50',
        'salmon': '#FA8072',
        'khaki': '#F0E68C',
        'violet': '#EE82EE',
        'indigo': '#4B0082',
        'turquoise': '#40E0D0',
        'crimson': '#DC143C',
        'beige': '#F5F5DC',
        'ivory': '#FFFFF0',
        'lavender': '#E6E6FA',
        'mint': '#98FB98',
        'peach': '#FFCBA4',
        'rose': '#FF66CC',
        'sky': '#87CEEB',
        'forest': '#228B22',
        'royal': '#4169E1'
    };

    const nameField = $('#id_name');
    const colorField = $('#id_color');

    if (nameField.length && colorField.length) {
        nameField.on('input blur', function() {
            const name = $(this).val().toLowerCase().trim();
            
            // Check if the name matches any color in our map
            for (const colorName in colorMap) {
                if (name.includes(colorName)) {
                    colorField.val(colorMap[colorName]);
                    break;
                }
            }
        });
    }
});