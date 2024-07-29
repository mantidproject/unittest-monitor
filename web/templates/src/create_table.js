create_table(table_name) {
    var table = $('#table-combined-{{ os_name }}').DataTable({
            "ajax": '../data/combined/{{json_file_name}}', // the path is preset here except the file name
            order: [[3, 'desc']],
            "columns": [
            {
                className: 'dt-control',
                orderable: false,
                data: null,
                defaultContent: '',
            },
            { data: 'test_name',title: "Test Name" },
            { data:  function( row, type, set ) {
              return Object.keys(row.past_failed_outcome).length;
            },
            title: "Count"
            },
            { data: 'last_fail_detected',title: "Last Failed Date" },
            ]
};
