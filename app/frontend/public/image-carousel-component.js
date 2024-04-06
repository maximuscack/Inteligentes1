import { Streamlit } from "streamlit-component-lib"
import React from "react"
import Carousel from "react-bootstrap/Carousel"

class ImageCarouselComponent extends React.Component {

  constructor(props) {
    super(props)
    this.state = {
      selectedImageUrl: null
    }
  }

  componentDidMount() {
    Streamlit.setFrameHeight(300)
  }

  render() {
    return (
      <Carousel>
        {this.props.args["imageUrls"].map((imageUrl, index) => (
          <Carousel.Item key={index}>
            <img
              className="d-block w-100"
              src={imageUrl}
              alt={`Slide ${index}`}
              onClick={() => {
                this.setState({ selectedImageUrl: imageUrl })
                Streamlit.setComponentValue(imageUrl)
              }}
            />
          </Carousel.Item>
        ))}
      </Carousel>
    )
  }
}

Streamlit.registerComponent(ImageCarouselComponent)
