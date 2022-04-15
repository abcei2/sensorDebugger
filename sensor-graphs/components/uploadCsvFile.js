import React, { useEffect, useState } from "react";
import { FileUploader } from "react-drag-drop-files";

import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Tooltip,
    Legend,
} from 'chart.js'
import { Line } from 'react-chartjs-2'


ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Tooltip,
    Legend
)

const numericColumns = ["DESIRED", "VALUE", "TEMP"]

const fileTypes = ["CSV"];

function randomRgba() {
    var o = Math.round, r = Math.random, s = 255;
    return 'rgba(' + o(r() * s) + ',' + o(r() * s) + ',' + o(r() * s) + ',' + r().toFixed(1) + ')';
}

const csvToJson = (csvFile) => {
    var array = csvFile.toString().split("\n");
    let headers = array.splice(0, 1)[0].split(",");
    let result = {};
    headers.map(header => {
        result[header] = []
    })
    array.map(item => {
        let values = item.split(",")
        values.map((value, index) => {
            if (numericColumns.includes(headers[index])) {
                if (!isNaN(parseFloat(value))) {
                    result[headers[index]].push(parseFloat(value))
                }

            }
            else if (headers[index] === "TIMESTAMP")
                result[headers[index]].push(new Date(value).toLocaleString())
            else if (headers[index] === "GOING")
                result[headers[index]].push(value === "UP" ? 1 : 0)
        })
    })

    return result
}

const UploadCSVFile = () => {
    const [file, setFile] = useState(null);
    const [chartData, setChartData] = useState({
        datasets: [],
    })

    const handleChange = (file) => {


        setFile(file);
    };
    useEffect(() => {

        if (file) {

            const read = new window.FileReader();
            read.readAsBinaryString(file);

            read.onloadend = function () {
                const csvData = csvToJson(read.result)
                const datasets = []
                for (let key in csvData) {
                    if (key !== "TIMESTAMP")
                        datasets.push({
                            label: key,
                            data: csvData[key],
                            borderColor: randomRgba()
                        })
                }
                const data = {
                    labels: csvData["TIMESTAMP"],
                    datasets,
                }

                setChartData({
                    ...data,
                    datasets: data.datasets.map((dataset) => ({
                        ...dataset,
                        tension: 0.4,
                    })),
                })
            }
        }
    }, [file])

    const options = {
        plugins: {
            legend: {
                display: true,
            },
        },
    }
    const chartLine = () => {
        return <div style={{
            position: "relative",
            textAlign: "center",
        }}>
            <Line type="line" data={chartData} options={options} />
        </div>
    }
    const dragAndDropHere = () => {
        return <div style={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            textAlign: "center",
            minHeight: !file ? "100vh" : ""
        }}>
            <FileUploader handleChange={handleChange} name="file" types={fileTypes} />
        </div>

    }
    return (
        <div >
            {dragAndDropHere()}
            {file && chartLine()}



        </div>
    );
}

export default UploadCSVFile;