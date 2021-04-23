function displayData(){
		let id = document.getElementById("id").value
		// console.log(input);
		fetch('/product?id='+id,{
			method:'GET'
		}).then(function(response){
			return response.json()
		}).then(function(jsonResponse){
			let table = document.getElementById("prodTable")
			table.innerHTML = ""
			for (var key in jsonResponse){
				if(key != "size_chart" && key!="size-driver" && key!="size_chart_table_centimeters" && key!="_attachments" && key!="_etag" && key!="_rid" && key!="_self" && key!="_ts" && key!="images-blob"){
					let row = document.createElement("TR")
					let data1 = document.createElement("TD")
					let data2 = document.createElement("TD")
					let text1 = document.createTextNode(key)
					let text2 = document.createTextNode(jsonResponse[key])
					data1.append(text1)
					data2.append(text2)
					row.append(data1)
					row.append(data2)
					table.append(row)
				}
			}
			let sizeChart = document.getElementById("sizeChart");
			let size_json = jsonResponse["size_chart"];
			console.log(size_json)
			let columns = Object.keys(size_json["0"])
			let row = document.createElement("TR")
			for (var idx in columns){
				let data = document.createElement("TH")
				let text = document.createTextNode(columns[idx])
				data.append(text)
				row.append(data)

			}
			sizeChart.append(row)
			console.log(columns)
			for (var key in size_json){
				row = document.createElement("TR")
				for (var idx in columns){
					// console.log(column)
					let data = document.createElement("TD")
					let text = document.createTextNode(size_json[key][columns[idx]])
					data.append(text)
					row.append(data)
				}
				sizeChart.append(row)
			}
		})	
	}