import React, { useEffect, useState, useReducer } from "react";

import { Input, Row, Slider, Col } from "antd";

import Select from "react-select";

import Button from "antd/es/button";

import { Formik, Form, Field } from "formik";

const { TextArea } = Input;

const models = [
  {value: 'rnnie.coref', label: "Open Information Extraction"}
]


const ieServiceRoute = "/api/iepredict/"
const getPrediction = async (values) => {
  const resp = await fetch(ieServiceRoute, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(values)
  });
  return await resp.json();
}

const SelectField = ({
  options,
  field,
  form,
}) => (
  <Select
    options={options}
    name={field.name}
    value={options ? options.find(option => option.value === field.value) : ''}
    onChange={(option) => form.setFieldValue(field.name, option.value)}
    onBlur={field.onBlur}
  />
)


const SliderField = ({
  step,
  min,
  max,
  defaultValue,
  field,
  form
}) => (
  <>
  <Slider
    defaultValue={defaultValue}
    onChange={(value) => form.setFieldValue(field.name, value)}
    value={field.value}
    min={min}
    max={max}
    step={step}
  />
  </>
)


const InputForm = ({updateGraph}) => {
  return (
    <div>
      <Formik
        initialValues={
          {
            text: "",
            model:models[0].value,
            levenshtein: 0.2,
          }
        }
        onSubmit={async (values, { setSubmitting }) => {
          const graph = await getPrediction(values)
          updateGraph(graph)
          setSubmitting(false)
        }}
      >
        {({ isSubmitting, values, setFieldValue }) => {
          return (
            <Form>
              <Row>
                <label htmlFor={'model'}>Select analysis model</label>
                <Field name={'model'} component={SelectField} options={models} />
              <Row/>
              <Row>
                <Col
                  span={12}
                >
                <Button
                  loading={isSubmitting}
                  type={'primary'}
                  disabled={!values.text.length}
                  htmlType={'submit'}
                  block
                  style={{
                    height: 38
                  }}
                >
                  Analyze text
                </Button>
                </Col>
                <Col
                 span={12}
                >

                {/*<Button*/}
                  {/*onClick={() => setFieldValue('text', demoText)}*/}
                  {/*block*/}
                {/*>*/}
                  {/*Use Demo Text*/}
                {/*</Button>*/}
                <Select
                  placeholder={"Select demo text..."}
                  options={demoTexts}
                  onChange={(option) => setFieldValue('text', option.value) }
                  style={{height:13}}
                />
                </Col>
              </Row>
                <label
                  htmlFor={'levenshtein'}
                >
                  Levenshtein percentage
                </label>
                <Field
                  name={'levenshtein'}
                  component={SliderField}
                  defaultValue={0.8}
                  min={0}
                  max={0.5}
                  step={0.01}
                />
              </Row>
              <label htmlFor={"text"}>Enter Text</label>
              <TextArea
                autosize={{minRows: 25}}
                value={values.text}
                name={"text"}
                onChange={e => setFieldValue('text', e.target.value)}
              />
            </Form>
          )
        }}

      </Formik>
    </div>
  )
}

const demoText = "When a T-cell encounters a foreign pathogen, it extends a vitamin D receptor. This is essentially a signaling device that allows the T-cell to bind to the active form of vitamin D, the steroid hormone calcitriol. T-cells have a symbiotic relationship with vitamin D. Not only does the T-cell extend a vitamin D receptor, in essence asking to bind to the steroid hormone version of vitamin D, calcitriol, but the T-cell expresses the gene CYP27B1, which is the gene responsible for converting the pre-hormone version of vitamin D, calcidiol into the steroid hormone version, calcitriol. Only after binding to calcitriol can T-cells perform their intended function. Other immune system cells that are known to express CYP27B1 and thus activate vitamin D calcidiol, are dendritic cells, keratinocytes and macrophages."

const immuneText2 = "Inflammation is one of the first responses of the immune system to infection. The symptoms of inflammation are redness, swelling, heat, and pain, which are caused by increased blood flow into tissue. Inflammation is produced by eicosanoids and cytokines, which are released by injured or infected cells. Eicosanoids include prostaglandins that produce fever and the dilation of blood vessels associated with inflammation, and leukotrienes that attract certain white blood cells (leukocytes). Common cytokines include interleukins that are responsible for communication between white blood cells; chemokines that promote chemotaxis; and interferons that have anti-viral effects, such as shutting down protein synthesis in the host cell. Growth factors and cytotoxic factors may also be released. These cytokines and other chemicals recruit immune cells to the site of infection and promote healing of any damaged tissue following the removal of pathogens."

const pharmacyText1 = "Pharmacists are healthcare professionals with specialised education and training who perform various roles to ensure optimal health outcomes for their patients through the quality use of medicines. Pharmacists may also be small-business proprietors, owning the pharmacy in which they practice. Since pharmacists know about the mode of action of a particular drug, and its metabolism and physiological effects on the human body in great detail, they play an important role in optimisation of a drug treatment for an individual."

const nytText1 = "The threat by the chairman, Representative Jerrold Nadler, Democrat of New York, came on the eve of Democrats’ return to Washington after a two-week congressional recess that has been dominated by questions about the special counsel’s report. Mr. Barr is scheduled to come before Mr. Nadler’s committee on Thursday to testify about it.\n" +
  "\n" +
  "But Mr. Barr and Democrats are at loggerheads over the Democrats’ proposed format for questioning him, and now the much-anticipated hearing is in doubt. The dispute spilled out into the open on Sunday when Democrats revealed that Mr. Barr was threatening to skip the session if they did not change their terms. Mr. Nadler said they have no intention of doing so.\n" +
  "\n" +
  "“The witness is not going to tell the committee how to conduct its hearing, period,” he told CNN on Sunday morning. If Mr. Barr does not show up, Mr. Nadler added, “then we will have to subpoena him, and we will have to use whatever means we can to enforce the subpoena.”\n" +
  "\n"

const demoTexts = [
  {
    "label": "SQUAD Immune 1",
    "value": demoText
  },
  {
    "label": "SQUAD Immune 2",
    "value": immuneText2
  },
  {
    "label": "SQUAD Pharmacy",
    "value": pharmacyText1
  },
  {
    "label": "New York Times",
    "value": nytText1
  }
]

export default InputForm
