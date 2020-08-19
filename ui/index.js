Vue.use(vuescroll);

var cotoprices = new Vue({
    el: '#cotoprices',
    data: {
        prices: [],
        filterDate: dayjs().format("YYYY-MM-DD"),
        ops: {
            rail: {
                opacity: '0.1',
                background: undefined,
                border: '0px solid #cecece',
                size: '6px'
            },
            bar: {
                background: '#f7f1f1',
                keepShow: false,
                size: '6px',
                minSize: 0.2
            },
            scrollButton: {
                enable: false,
                background: '#cecece'
            },
            scrollPanel: {
                easing: 'easeInQuad',
                speed: 800
            },
            vuescroll: {
                wheelScrollDuration: 0,
                wheelDirectionReverse: false
            }
        }
    },
    mounted () {
        let query = 'query MyQuery ($date:date){' +
                '   variation(order_by: {diff: desc}, where: {date: {_eq: $date}}) {' +
                '       date,productshopid,price,diff,product {name,url}' +
                '   }' +
                '}';

        const url = "http://ec2-3-17-64-92.us-east-2.compute.amazonaws.com:8085/v1/graphql";

        const opts = {
            method: "POST",
            headers: { "Content-Type": "application/json"},
            body: JSON.stringify({ query: query, variables: {"date":this.filterDate} })
        };

        fetch(url, opts)
            .then(res => res.json())
            .then(res => {this.prices = res.data.variation;})
            .catch(console.error);
    },
    methods: {
        twoDecimals: function(number) {
            return number.toFixed(2);
        },
        getDiffClass: function(number) {
            if(number > 0) return 'diffPositive'

            return 'diffNegative'
        }
    }
});